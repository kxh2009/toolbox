# AGENTS.md

个人工具箱（toolbox）。Codex 可以直接运行本仓库中的脚本，无需额外引导。

## 目录结构

- `security/` — 授权范围内的安全测试脚本
  - `port_scan.py` — 多线程端口扫描（`--ports 1-1000` / `--top 20|50|100`）
  - `subdomain_enum.py` — 子域名枚举（内置字典，支持 `--wordlist`）
  - `dir_brute.py` — Web 目录爆破（支持 `--extensions php,html`）
- `video-gen/`
  - `batch_gen.py` — 批量视频生成（需要 `VIDEO_API_KEY` 或 `--api-key`）
  - `prompts.md` — 提示词模板库
- `agnes-proxy/agnes_proxy.py` — Agnes 模型映射代理（`127.0.0.1:8765`）

## 运行依赖

```bash
python3 -m pip install --user -r requirements.txt
```

仅需 `requests`（用于 `dir_brute.py` 和 `batch_gen.py`）。其余脚本只用标准库。

## 常用命令

```bash
python3 security/port_scan.py example.com --top 50
python3 security/subdomain_enum.py example.com
python3 security/dir_brute.py https://example.com --extensions php,html
python3 video-gen/batch_gen.py --prompts video-gen/prompts.md --output ./videos
python3 agnes-proxy/agnes_proxy.py
```

## 约定

- 安全脚本**仅用于已授权目标**（自有资产、授权渗透测试、CTF、本地实验环境）。
- 端口扫描 / 目录爆破需要**出网权限**；Codex 沙箱默认禁网，需要时提权运行。
- 扫描结果默认打印到终端，可用 `--output` 落盘；产物目录已在 `.gitignore` 中忽略。
- 提交信息用中文简述改动即可，分支前缀默认 `codex/`。
