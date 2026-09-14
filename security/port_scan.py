#!/usr/bin/env python3
"""
端口扫描器 - 仅用于授权测试
快速扫描目标主机的开放端口

用法:
    python3 port_scan.py example.com
    python3 port_scan.py 192.168.1.1 --ports 1-1000
    python3 port_scan.py example.com --top 100 --timeout 1
"""

import socket
import argparse
import concurrent.futures
from datetime import datetime


# 常用端口及服务映射
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 9090: "WebAdmin",
    27017: "MongoDB", 9200: "Elasticsearch", 5601: "Kibana",
}

TOP_100 = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
           993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9090]


def scan_port(host: str, port: int, timeout: float = 1.0) -> tuple:
    """扫描单个端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            service = COMMON_PORTS.get(port, "unknown")
            return (port, True, service)
        return (port, False, "")
    except socket.error:
        return (port, False, "")


def parse_ports(port_str: str) -> list:
    """解析端口范围，如 '1-1000' 或 '22,80,443'"""
    ports = []
    for part in port_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return ports


def main():
    parser = argparse.ArgumentParser(description="端口扫描器（仅用于授权测试）")
    parser.add_argument("host", help="目标主机")
    parser.add_argument("--ports", help="端口范围，如 1-1000 或 22,80,443")
    parser.add_argument("--top", type=int, choices=[20, 50, 100],
                       help="扫描 Top N 常用端口")
    parser.add_argument("--timeout", type=float, default=1.0,
                       help="超时时间(秒)")
    parser.add_argument("--threads", type=int, default=50,
                       help="并发线程数")
    args = parser.parse_args()

    # 确定端口列表
    if args.ports:
        ports = parse_ports(args.ports)
    elif args.top:
        ports = TOP_100[:args.top]
    else:
        ports = TOP_100

    print(f"开始扫描 {args.host}，共 {len(ports)} 个端口")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_port, args.host, p, args.timeout): p
                  for p in ports}
        for future in concurrent.futures.as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append((port, service))
                print(f"  端口 {port:>5} 开放 - {service}")

    print("-" * 50)
    print(f"扫描完成，发现 {len(open_ports)} 个开放端口")
    if not open_ports:
        print("（未发现开放端口，可能被防火墙拦截）")


if __name__ == "__main__":
    main()
