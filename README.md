# 🧰 kxh2009's Toolbox

个人工具箱，收集实用脚本和工具。

## 📂 目录结构

```
toolbox/
├── video-gen/          # 视频生成相关
│   ├── prompts.md      # 提示词模板库
│   └── batch_gen.py    # 批量视频生成脚本
├── security/           # 安全测试工具（仅授权使用）
│   ├── README.md       # 使用说明
│   ├── port_scan.py    # 端口扫描器
│   ├── subdomain_enum.py  # 子域名枚举
│   └── dir_brute.py    # Web 目录爆破
├── agnes-proxy/        # Agnes 模型代理
│   ├── README.md       # 使用说明
│   └── agnes_proxy.py  # 代理脚本
└── README.md           # 本文件
```

## 🎬 video-gen - 视频生成

- **prompts.md**：5 大类视频生成提示词模板（产品展示、人物口播、风景空镜、科技感、美食）
- **batch_gen.py**：批量调用视频生成 API，支持从文件读取提示词、自动下载、结果记录

## 🔒 security - 安全工具

> ⚠️ 仅用于授权范围内的安全测试

- **port_scan.py**：多线程端口扫描，支持端口范围和 Top N 常用端口
- **subdomain_enum.py**：子域名枚举，内置 100+ 常用子域名字典
- **dir_brute.py**：Web 目录爆破，发现隐藏路径、备份文件、配置泄露

## 🤖 agnes-proxy - Agnes 模型代理

让 Codex 等工具接入 Agnes 免费模型的本地代理，自动处理模型名映射、参数降级和工具过滤。

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/kxh2009/toolbox.git
cd toolbox

# 安装依赖
pip3 install requests

# 运行端口扫描
python3 security/port_scan.py example.com --top 50

# 子域名枚举
python3 security/subdomain_enum.py example.com

# 目录爆破
python3 security/dir_brute.py https://example.com
```

## 📝 License

MIT
