#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话学习测试脚本
从 JSON 文件中读取对话并学习
"""

import json
import sys
import os

# 导入技能模块
from knowledge_base import KnowledgeBase
from conversation_learner import ConversationLearner

def load_config():
    """加载配置"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.normpath(os.path.join(script_dir, '..', 'config', 'config.json'))

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def main():
    # 加载配置和初始化
    config = load_config()
    kb = KnowledgeBase(config.get("knowledge_base", {}).get(
        "storage_path", "./knowledge/knowledge_db.json"
    ), config)
    learner = ConversationLearner(config)

    # 读取对话文件
    conv_file = "./docs/conversation-info.json"
    with open(conv_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conversation = data["conversation"]
    print(f"📝 读取到 {len(conversation)} 条对话消息")

    # 分析对话并提取知识
    knowledge_items = learner.analyze_conversation(
        conversation,
        conversation_id="test_conv_20260515"
    )

    print(f"🧠 提取到 {len(knowledge_items)} 条知识单元\n")

    # 添加到知识库
    added_count = 0
    for item in knowledge_items:
        success, msg, _ = kb.add_knowledge(
            content=item["content"],
            summary=item["content"][:50],
            tags=item.get("tags", []),
            source_type="conversation",
            context=f"对话ID: {item['conversation_id']}",
            confidence=item.get("confidence", 0.7)
        )

        if success:
            added_count += 1
            print(f"✅ 添加: {item['content'][:60]}...")
            print(f"   置信度: {item.get('confidence', 0):.2f}, 模式: {', '.join(item.get('patterns_matched', []))}\n")
        else:
            print(f"⚪ 跳过（重复）: {item['content'][:50]}...\n")

    print(f"\n📊 总结：添加了 {added_count}/{len(knowledge_items)} 条新知识")
    print(f"   知识库总数: {len(kb.units)}")

    # 显示统计
    stats = kb.get_statistics()
    print(f"\n最新统计:")
    print(f"  总单元: {stats['total_units']}")
    print(f"  来源: {stats['sources']}")

if __name__ == "__main__":
    main()
