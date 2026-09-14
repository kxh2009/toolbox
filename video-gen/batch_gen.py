#!/usr/bin/env python3
"""
批量视频生成脚本
支持从文本文件读取提示词，批量调用视频生成 API

用法:
    python3 batch_gen.py --prompts prompts.txt --output ./output
    python3 batch_gen.py --prompt "a cat playing piano" --output ./output
"""

import argparse
import os
import time
import json
import requests
from pathlib import Path


def generate_video(prompt: str, api_key: str, base_url: str, model: str = "seedance-2.0",
                   duration: int = 5, resolution: str = "1080p") -> dict:
    """调用视频生成 API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution
    }
    try:
        resp = requests.post(f"{base_url}/v1/videos/generations",
                           headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def download_video(url: str, output_path: str) -> bool:
    """下载生成的视频"""
    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="批量视频生成工具")
    parser.add_argument("--prompts", help="提示词文件路径（每行一个）")
    parser.add_argument("--prompt", help="单个提示词")
    parser.add_argument("--output", default="./videos", help="输出目录")
    parser.add_argument("--api-key", default=os.getenv("VIDEO_API_KEY", ""),
                       help="API Key（或设环境变量 VIDEO_API_KEY）")
    parser.add_argument("--base-url", default="https://api.example.com",
                       help="API 基础地址")
    parser.add_argument("--model", default="seedance-2.0", help="模型名称")
    parser.add_argument("--duration", type=int, default=5, help="视频时长(秒)")
    parser.add_argument("--delay", type=float, default=2.0,
                       help="每次请求间隔(秒)，避免触发限流")
    args = parser.parse_args()

    if not args.api_key:
        print("错误: 请设置 --api-key 或环境变量 VIDEO_API_KEY")
        return

    # 收集提示词
    prompts = []
    if args.prompts:
        with open(args.prompts, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
    elif args.prompt:
        prompts = [args.prompt]
    else:
        print("错误: 请提供 --prompts 或 --prompt")
        return

    os.makedirs(args.output, exist_ok=True)
    print(f"共 {len(prompts)} 个提示词，开始生成...")

    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] {prompt[:60]}...")
        result = generate_video(prompt, args.api_key, args.base_url,
                               args.model, args.duration)

        if "error" in result:
            print(f"  失败: {result['error']}")
            results.append({"prompt": prompt, "status": "failed",
                          "error": result["error"]})
        else:
            video_url = result.get("data", [{}])[0].get("url", "")
            if video_url:
                filename = f"video_{i:03d}.mp4"
                filepath = os.path.join(args.output, filename)
                if download_video(video_url, filepath):
                    print(f"  已保存: {filepath}")
                    results.append({"prompt": prompt, "status": "success",
                                  "file": filepath})
                else:
                    results.append({"prompt": prompt, "status": "download_failed"})
            else:
                print(f"  任务已提交: {result}")
                results.append({"prompt": prompt, "status": "submitted",
                              "data": result})

        if i < len(prompts):
            time.sleep(args.delay)

    # 保存结果
    result_file = os.path.join(args.output, "results.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n完成！结果保存在: {result_file}")


if __name__ == "__main__":
    main()
