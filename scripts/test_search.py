#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# 正确添加路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, '..'))

import json
from knowledge_base import KnowledgeBase

# 加载配置
config_path = os.path.join(script_dir, '..', 'config', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

storage_path = os.path.join(script_dir, '..', 'knowledge', 'knowledge_db.json')
kb = KnowledgeBase(storage_path, config)

print(f"Loaded {len(kb.units)} units")

query = "Agent"
results = kb.search(query)

print(f"\nSearch for '{query}': {len(results)} results")
for r in results[:3]:
    print(f"- {r['summary'][:60]} (score: {r['relevance_score']:.3f})")
