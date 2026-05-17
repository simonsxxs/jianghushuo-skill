#!/usr/bin/env python3
"""
批量获取姜胡说所有内容并保存为 markdown
"""
import json
import subprocess
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

OUTPUT_DIR = Path("/Users/simon-mac/project/蒸馏人物、主题/姜胡说_raw")
TOPIC_ID = "pn5LPKZJ"
FOLLOW_ID = "1224193"
MAX_WORKERS = 5  # 并发数

def run_cmd(cmd):
    """运行 getnote 命令并返回 JSON 结果"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"JSON parse error: {result.stdout[:200]}")
        return None

def fetch_all_content_ids():
    """获取所有内容的 post_id_alias 列表"""
    all_contents = []
    page = 1
    while True:
        print(f"Fetching page {page}...")
        cmd = f'getnote kb blogger-contents {TOPIC_ID} {FOLLOW_ID} --page {page} -o json'
        data = run_cmd(cmd)
        if not data or not data.get("success"):
            print(f"Failed to fetch page {page}")
            break

        contents = data["data"]["contents"]
        if not contents:
            break

        for item in contents:
            all_contents.append({
                "post_id_alias": item["post_id_alias"],
                "post_title": item["post_title"],
                "post_summary": item.get("post_summary", ""),
                "post_type": item.get("post_type", ""),
            })

        if not data["data"].get("has_more", False):
            break
        page += 1

    print(f"Total content items: {len(all_contents)}")
    return all_contents

def fetch_single_content(item):
    """获取单条完整内容"""
    post_id = item["post_id_alias"]
    filepath = OUTPUT_DIR / f"{post_id}.md"

    # 如果已存在则跳过
    if filepath.exists():
        return f"SKIP: {post_id}"

    cmd = f'getnote kb blogger-content {TOPIC_ID} {post_id} -o json'
    data = run_cmd(cmd)

    if not data or not data.get("success"):
        return f"FAIL: {post_id}"

    content_data = data.get("data", {})

    # 构建 markdown 内容
    md_content = f"""# {item['post_title']}

**类型**: {item['post_type']}
**ID**: {post_id}

## AI 摘要

{item['post_summary']}

## 完整内容

{content_data.get('post_media_text', content_data.get('post_summary', '无内容'))}
"""

    filepath.write_text(md_content, encoding="utf-8")
    return f"OK: {post_id}"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 第一步：获取所有内容 ID
    print("=" * 50)
    print("Step 1: Fetching all content IDs...")
    print("=" * 50)
    all_items = fetch_all_content_ids()

    # 保存索引文件
    index_path = OUTPUT_DIR / "_index.json"
    index_path.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index saved to {index_path}")

    # 第二步：并行获取完整内容
    print("=" * 50)
    print(f"Step 2: Fetching full content (workers={MAX_WORKERS})...")
    print("=" * 50)

    ok_count = 0
    fail_count = 0
    skip_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_single_content, item): item for item in all_items}

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result.startswith("OK"):
                ok_count += 1
            elif result.startswith("SKIP"):
                skip_count += 1
            else:
                fail_count += 1

            if (i + 1) % 20 == 0 or i == len(futures) - 1:
                print(f"Progress: {i+1}/{len(futures)} | OK: {ok_count} | SKIP: {skip_count} | FAIL: {fail_count}")

    print("=" * 50)
    print(f"Done! OK: {ok_count}, SKIP: {skip_count}, FAIL: {fail_count}")
    print(f"Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
