#!/usr/bin/env python3
"""
Agnes 模型映射代理
把 Codex App 发来的 OpenAI 模型名（gpt-6-astra 等）映射为 agnes-2.0-flash，
转发到 Agnes API，支持流式响应（SSE）。
"""
import json
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

UPSTREAM = "https://apihub.agnes-ai.com"
TARGET_MODEL = "agnes-2.0-flash"
LISTEN_PORT = 8765

# 不替换模型名的路径
SKIP_MODEL_REWRITE = {"/v1/models"}


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        sys.stderr.write("[proxy] %s - %s\n" % (self.address_string(), format % args))

    def _forward(self, method):
        path = self.path
        url = UPSTREAM + path

        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # 替换模型名和 effort 字段
        if path not in SKIP_MODEL_REWRITE and body:
            try:
                data = json.loads(body)
                old_model = data.get("model", "")
                if old_model and old_model != TARGET_MODEL:
                    data["model"] = TARGET_MODEL
                    sys.stderr.write(f"[proxy] model rewrite: {old_model} -> {TARGET_MODEL}\n")
                # 递归替换所有 effort 字段：Agnes 只支持 minimal/low/medium/high
                effort_map = {"xhigh": "high", "extra_high": "high", "extra-high": "high", "xlarge": "high"}
                def fix_effort(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k.lower() in ("effort", "reasoning_effort", "reasoningeffort"):
                                if isinstance(v, str) and v.lower() in effort_map:
                                    obj[k] = effort_map[v.lower()]
                                    sys.stderr.write(f"[proxy] effort rewrite: {v} -> {obj[k]}\n")
                            else:
                                fix_effort(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            fix_effort(item)
                fix_effort(data)
                # 过滤 Agnes 不支持的工具 type
                supported_tool_types = {"function", "web_search_preview", "code_interpreter", "mcp"}
                if "tools" in data and isinstance(data["tools"], list):
                    original_count = len(data["tools"])
                    data["tools"] = [t for t in data["tools"] if t.get("type") in supported_tool_types]
                    if len(data["tools"]) != original_count:
                        sys.stderr.write(f"[proxy] tools filtered: {original_count} -> {len(data['tools'])}\n")
                body = json.dumps(data).encode("utf-8")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        # 构建转发请求头
        headers = {}
        for key in ("Authorization", "Content-Type", "Accept", "OpenAI-Beta",
                     "OpenAI-Organization", "X-Request-Id", "anthropic-version"):
            val = self.headers.get(key)
            if val:
                headers[key] = val
        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        req = Request(url, data=body if method == "POST" else None,
                      headers=headers, method=method)

        try:
            resp = urlopen(req, timeout=120)
        except HTTPError as e:
            # 转发错误响应
            error_body = e.read()
            sys.stderr.write(f"[proxy] upstream error {e.code}: {error_body.decode('utf-8', errors='replace')[:500]}\n")
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() in ("content-type", "content-length"):
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
            return
        except URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            msg = json.dumps({"error": {"message": f"Upstream error: {e}", "type": "proxy_error"}}).encode()
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return

        # 转发响应头
        self.send_response(resp.status)
        content_type = resp.headers.get("Content-Type", "application/json")
        self.send_header("Content-Type", content_type)

        is_stream = "text/event-stream" in content_type or "stream" in content_type.lower()

        if is_stream:
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            # 逐块转发流式响应
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                # 写入 chunked 格式
                self.wfile.write(b"%x\r\n" % len(chunk))
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
        else:
            resp_body = resp.read()
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

    def do_GET(self):
        self._forward("GET")

    def do_POST(self):
        self._forward("POST")

    def do_PUT(self):
        self._forward("PUT")

    def do_DELETE(self):
        self._forward("DELETE")


def main():
    server = HTTPServer(("127.0.0.1", LISTEN_PORT), ProxyHandler)
    sys.stderr.write(f"[proxy] Agnes model mapping proxy listening on http://127.0.0.1:{LISTEN_PORT}\n")
    sys.stderr.write(f"[proxy] Upstream: {UPSTREAM}, target model: {TARGET_MODEL}\n")
    server.serve_forever()


if __name__ == "__main__":
    main()
