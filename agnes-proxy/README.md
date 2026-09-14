# Agnes 模型代理

让 Codex 等工具接入 Agnes 免费模型的本地代理。

## 功能
- 模型名自动映射（任何 OpenAI 模型名 → agnes-2.0-flash）
- effort 参数自动降级（xhigh/extra_high → high）
- 工具过滤（过滤 Agnes 不支持的工具类型）
- 兼容 OpenAI Responses API

## 使用方法

### 1. 启动代理
```bash
python3 agnes_proxy.py
```
默认监听 `127.0.0.1:8765`

### 2. 配置环境变量
```bash
export AGNES_API_KEY="sk-你的key"
export AGNES_BASE_URL="https://apihub.agnes-ai.com/v1"
export AGNES_MODEL="agnes-2.0-flash"
```

### 3. Codex 配置
在 `~/.codex/config.toml` 中：
```toml
model_provider = "custom"
base_url = "http://127.0.0.1:8765/v1"
wire_api = "responses"
namespace_tools = false
```

### 4. 开机自启动（macOS）
创建 `~/Library/LaunchAgents/com.user.agnesproxy.plist`：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.agnesproxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/你的用户名/.codex/agnes_proxy.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/agnes_proxy.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/agnes_proxy.log</string>
</dict>
</plist>
```
加载：`launchctl load ~/Library/LaunchAgents/com.user.agnesproxy.plist`

## 注意
- Agnes 免费版 RPM 限制较低（约每分钟 3-5 次），连续请求可能触发 429
- 国际站端点 `apihub.agnes-ai.com`，中国站 `api.agnes-ai.cn`
