# 安全工具集

> ⚠️ **免责声明**：以下工具仅用于**授权范围内**的安全测试和学习研究。未经授权对他人系统进行扫描属于违法行为。使用者需自行承担法律责任。

## 工具列表

### 1. port_scan.py - 端口扫描器
快速扫描目标主机的开放端口和服务。

```bash
# 扫描常用端口
python3 port_scan.py example.com

# 指定端口范围
python3 port_scan.py 192.168.1.1 --ports 1-1000

# 扫描 Top 100 端口
python3 port_scan.py example.com --top 100

# 自定义超时和线程
python3 port_scan.py example.com --timeout 2 --threads 100
```

### 2. subdomain_enum.py - 子域名枚举
通过字典爆破发现目标域名的子域名。

```bash
# 使用内置字典
python3 subdomain_enum.py example.com

# 使用自定义字典
python3 subdomain_enum.py example.com --wordlist subdomains.txt

# 保存结果
python3 subdomain_enum.py example.com --output results.txt
```

### 3. dir_brute.py - Web 目录爆破
发现网站的隐藏目录、备份文件、配置文件等。

```bash
# 基础扫描
python3 dir_brute.py https://example.com

# 指定扩展名
python3 dir_brute.py https://example.com --extensions php,html,txt,bak

# 自定义字典
python3 dir_brute.py https://example.com --wordlist dirs.txt
```

## 合法使用场景
- 自己拥有的服务器/网站的安全自查
- 企业授权的渗透测试
- CTF 比赛环境
- 本地实验环境

## 禁止用途
- 扫描未授权的第三方系统
- 配合漏洞利用进行攻击
- 任何违反《网络安全法》的行为
