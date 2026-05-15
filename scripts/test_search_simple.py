#!/usr/bin/env python3
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, '..'))

import json
from knowledge_base import KnowledgeBase

# 加载配置
config_path = os.path.join(script_dir, '..', 'config', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 调整搜索配置
config['search']['min_similarity_score'] = 0.05  # Very low threshold

storage_path = os.path.join(script_dir, '..', 'knowledge', 'knowledge_db.json')
kb = KnowledgeBase(storage_path, config)

query = "agent"
results = kb.search(query, max_results=5)

# 将输出写入文件避免编码问题
with open('search_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"Query: {query}\n")
    f.write(f"Results: {len(results)}\n\n")
    for i, r in enumerate(results, 1):
        f.write(f"[{i}] {r['summary']}\n")
        f.write(f"    Score: {r['relevance_score']:.4f}\n")
        f.write(f"    Tags: {r['tags']}\n")
        f.write(f"    Content: {r['content'][:200]}...\n\n")

print("Results written to search_results.txt")
