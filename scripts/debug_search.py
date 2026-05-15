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
storage_path = config.get("knowledge_base", {}).get(
    "storage_path", "./knowledge/knowledge_db.json"
)
storage_path = os.path.join(parent_dir, storage_path)

kb = KnowledgeBase(storage_path, config)

print(f"知识库共 {len(kb.units)} 个单元\n")

# 搜索 "Agent"
query = "Agent"
print(f"搜索词: '{query}'\n")

results = kb.search(query)

print(f"找到 {len(results)} 条结果:\n")
for i, r in enumerate(results, 1):
    print(f"[{i}] ID: {r['id']}")
    print(f"    摘要: {r['summary']}")
    print(f"    内容: {r['content'][:200]}")
    print(f"    标签: {r['tags']}")
    print(f"    相关度: {r['relevance_score']:.4f}")
    print()

# 检查包含 "Agent" 的单元
print("\n=== 检查包含 'agent'（小写）的单元 ===")
for unit in kb.units.values():
    if 'agent' in unit.content.lower():
        print(f"ID: {unit.id}")
        print(f"内容片段: ...{unit.content[unit.content.lower().find('agent')-30:unit.content.lower().find('agent')+50]}...")
        print()
