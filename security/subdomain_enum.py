#!/usr/bin/env python3
"""
子域名枚举工具 - 仅用于授权测试
通过字典爆破发现目标域名的子域名

用法:
    python3 subdomain_enum.py example.com
    python3 subdomain_enum.py example.com --wordlist subdomains.txt
    python3 subdomain_enum.py example.com --threads 30
"""

import socket
import argparse
import concurrent.futures
from datetime import datetime


# 内置常用子域名字典
DEFAULT_SUBDOMAINS = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
    "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig",
    "m", "imap", "test", "ns", "blog", "pop3", "dev", "www2", "admin",
    "forum", "news", "vpn", "ns3", "mail2", "new", "mysql", "old",
    "lists", "apps", "www3", "proxy", "ads", "host", "cms", "backup",
    "shop", "api", "cdn", "static", "media", "images", "img", "download",
    "docs", "doc", "wiki", "git", "gitlab", "jenkins", "ci", "cd",
    "staging", "prod", "production", "dev", "development", "test", "testing",
    "uat", "qa", "demo", "beta", "alpha", "stage", "lab", "sandbox",
    "internal", "intranet", "extranet", "portal", "dashboard", "panel",
    "console", "monitor", "grafana", "kibana", "prometheus", "zabbix",
    "redis", "mongo", "es", "elasticsearch", "rabbitmq", "kafka",
    "minio", "s3", "oss", "cdn", "waf", "firewall", "router", "switch",
    "printer", "camera", "iot", "gateway", "api", "graphql", "grpc",
    "ws", "websocket", "socket", "realtime", "push", "notify",
    "auth", "sso", "login", "register", "signup", "account", "user",
    "profile", "settings", "config", "env", "debug", "status",
    "health", "metrics", "trace", "log", "logs", "report", "stats",
    "admin", "manager", "manage", "backend", "cms", "wp", "wordpress",
    "drupal", "joomla", "magento", "shopify", "opencart", "prestashop",
]


def check_subdomain(domain: str, subdomain: str, timeout: float = 3.0) -> tuple:
    """检查子域名是否存在"""
    full = f"{subdomain}.{domain}"
    try:
        ip = socket.gethostbyname(full)
        return (full, ip, True)
    except socket.gaierror:
        return (full, "", False)


def main():
    parser = argparse.ArgumentParser(description="子域名枚举（仅用于授权测试）")
    parser.add_argument("domain", help="目标域名，如 example.com")
    parser.add_argument("--wordlist", help="自定义字典文件路径")
    parser.add_argument("--threads", type=int, default=20, help="并发线程数")
    parser.add_argument("--timeout", type=float, default=3.0, help="超时时间")
    parser.add_argument("--output", help="结果输出文件")
    args = parser.parse_args()

    # 加载字典
    if args.wordlist:
        with open(args.wordlist, "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]
    else:
        subdomains = DEFAULT_SUBDOMAINS

    print(f"开始枚举 {args.domain} 的子域名")
    print(f"字典大小: {len(subdomains)}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check_subdomain, args.domain, s, args.timeout): s
                  for s in subdomains}
        for future in concurrent.futures.as_completed(futures):
            sub, ip, exists = future.result()
            if exists:
                found.append((sub, ip))
                print(f"  发现: {sub} -> {ip}")

    print("-" * 50)
    print(f"完成，共发现 {len(found)} 个子域名")

    if args.output:
        with open(args.output, "w") as f:
            for sub, ip in found:
                f.write(f"{sub}\t{ip}\n")
        print(f"结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
