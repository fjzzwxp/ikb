#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from knowledge_base import KnowledgeBase

# 加载配置
config_path = os.path.join(parent_dir, 'config', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化知识库
relative_path = config.get("knowledge_base", {}).get(
    "storage_path", "./knowledge/knowledge_db.json"
)
storage_path = os.path.normpath(os.path.join(parent_dir, relative_path))
print(f"Knowledge base path: {storage_path}")
print(f"Exists: {os.path.exists(storage_path)}")

kb = KnowledgeBase(storage_path, config)

query = "Agent"
query_lower = query.lower()

for unit in kb.units.values():
    content_lower = unit.content.lower()
    summary_lower = unit.summary.lower()

    keyword_match = query_lower in content_lower or query_lower in summary_lower
    content_sim = kb._calculate_similarity(query, unit.content)
    summary_sim = kb._calculate_similarity(query, unit.summary) if unit.summary else 0

    print(f"ID: {unit.id}")
    print(f"内容包含'{query}': {keyword_match}")
    print(f"内容相似度: {content_sim:.4f}")
    print(f"摘要相似度: {summary_sim:.4f}")
    print(f"内容摘要: {unit.summary}\n")
