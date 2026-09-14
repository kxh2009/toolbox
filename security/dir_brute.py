#!/usr/bin/env python3
"""
Web 目录爆破工具 - 仅用于授权测试
通过字典发现目标网站的隐藏目录和文件

用法:
    python3 dir_brute.py https://example.com
    python3 dir_brute.py https://example.com --wordlist dirs.txt
    python3 dir_brute.py https://example.com --extensions php,html,txt
"""

import requests
import argparse
import concurrent.futures
from datetime import datetime
from urllib.parse import urljoin


# 内置常用目录字典
DEFAULT_DIRS = [
    "admin", "login", "wp-admin", "wp-login.php", "administrator",
    "backup", "backups", "bak", "old", "test", "dev", "staging",
    "config", "config.php", "configuration", "env", ".env",
    "phpinfo.php", "info.php", "test.php", "debug", "console",
    "shell", "cmd", "upload", "uploads", "files", "download",
    "api", "api/v1", "api/v2", "graphql", "swagger", "docs",
    ".git", ".git/config", ".git/HEAD", ".svn", ".hg",
    "robots.txt", "sitemap.xml", "crossdomain.xml", "clientaccesspolicy.xml",
    "wp-content", "wp-includes", "wp-json", "xmlrpc.php",
    "phpmyadmin", "pma", "mysql", "db", "database",
    "admin.php", "login.php", "index.php", "install.php",
    "setup.php", "upgrade.php", "readme.html", "license.txt",
    "composer.json", "package.json", "yarn.lock", "package-lock.json",
    "Dockerfile", "docker-compose.yml", ".dockerignore",
    "aws", "aws.json", "credentials", "secret", "secrets",
    "key", "keys", "pem", "crt", "cert", "ssl",
    "server-status", "server-info", "nginx_status", "status",
    "actuator", "actuator/health", "actuator/env", "actuator/heapdump",
    "jolokia", "metrics", "prometheus", "health", "healthz",
    "dashboard", "grafana", "kibana", "elasticsearch", "_search",
    "redis", "mongo", "rabbitmq", "management",
    "web.config", ".htaccess", ".htpasswd", "nginx.conf",
    "error.log", "access.log", "logs", "log", "debug.log",
    "tmp", "temp", "cache", "storage", "data",
    "public", "private", "protected", "internal",
    "assets", "static", "media", "images", "img", "css", "js",
    "fonts", "icons", "uploads", "files", "documents",
    "archive", "archives", "zip", "tar", "tar.gz", "rar",
    "backup.zip", "backup.tar.gz", "www.zip", "html.zip", "web.zip",
    "dump.sql", "database.sql", "db.sql", "backup.sql",
    "phpinfo", "test", "info", "phpmyadmin", "adminer",
]


def check_path(base_url: str, path: str, extensions: list,
               timeout: float = 5.0) -> tuple:
    """检查路径是否存在"""
    paths_to_check = [path]
    if extensions and "." not in path:
        for ext in extensions:
            paths_to_check.append(f"{path}.{ext}")

    for p in paths_to_check:
        url = urljoin(base_url + "/", p)
        try:
            resp = requests.get(url, timeout=timeout, allow_redirects=False,
                              headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code in [200, 301, 302, 401, 403]:
                return (url, resp.status_code, resp.headers.get("Content-Length", "?"))
        except requests.exceptions.RequestException:
            pass
    return (None, 0, "")


def main():
    parser = argparse.ArgumentParser(description="Web 目录爆破（仅用于授权测试）")
    parser.add_argument("url", help="目标 URL，如 https://example.com")
    parser.add_argument("--wordlist", help="自定义字典文件")
    parser.add_argument("--extensions", default="",
                       help="扩展名列表，如 php,html,txt")
    parser.add_argument("--threads", type=int, default=20, help="并发数")
    parser.add_argument("--timeout", type=float, default=5.0, help="超时时间")
    parser.add_argument("--output", help="结果输出文件")
    args = parser.parse_args()

    # 加载字典
    if args.wordlist:
        with open(args.wordlist, "r") as f:
            dirs = [line.strip() for line in f if line.strip()]
    else:
        dirs = DEFAULT_DIRS

    extensions = [e.strip() for e in args.extensions.split(",") if e.strip()]

    print(f"开始目录爆破: {args.url}")
    print(f"字典大小: {len(dirs)}，扩展名: {extensions or '无'}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check_path, args.url, d, extensions,
                                   args.timeout): d for d in dirs}
        for future in concurrent.futures.as_completed(futures):
            url, status, size = future.result()
            if url:
                found.append((url, status, size))
                print(f"  [{status}] {url}  ({size} bytes)")

    print("-" * 60)
    print(f"完成，发现 {len(found)} 个有效路径")

    if args.output:
        with open(args.output, "w") as f:
            for url, status, size in found:
                f.write(f"{status}\t{size}\t{url}\n")
        print(f"结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
