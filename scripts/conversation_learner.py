#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话学习器模块
从对话中提取和识别有价值的知识
"""

import re
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime


class ConversationLearner:
    """对话学习器类"""

    # 知识提取的模式（正则表达式）
    # 定义：识别定义、概念解释
    DEFINITION_PATTERNS = [
        r'([\u4e00-\u9fff]+(?:是指|是指的?|定义为?|的意思是?|解释为?|就是))\s*(.+)[。！？.!?]',
        r'(.+?)(?:是指|是指的?|定义为?|的意思是?|解释为?|就是)\s*([\u4e00-\u9fff].+?)[。！？.!?]',
        r'([\u4e00-\u9fff]+):\s*(.+?)(?:；|;|，|,|。|$)',
    ]

    # 事实陈述：识别事实性信息
    FACT_PATTERNS = [
        r'([\u4e00-\u9fff]+)(?:是|有|位于|属于|来自|成立于|创建于|发布于)\s*(.+?)[。！？.!?]',
        r'事实上[，,]?\s*(.+?)[。！？.!?]',
        r'根据[^,]*?，(.+?)[。！？.!?]',
    ]

    # 列表信息：识别列表项
    LIST_PATTERNS = [
        r'[（(](?:一|二|三|四|五|1|2|3|4|5)[）).]\s*(.+?)(?:[、，,]|$)',
        r'[（(]首先[）)]\s*(.+?)(?:然后|其次|最后|。|$)',
    ]

    # 德语/英语名词（可能为专有名词）
    ENGLISH_TERM_PATTERN = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get(
            "learning", {}).get("confidence_threshold", 0.7)
        self.auto_learn = self.config.get(
            "learning", {}).get("auto_learn_from_conversation", True)
        self.extract_patterns = self.config.get(
            "learning", {}).get("extract_conversation_patterns", True)

        # 停用词（过滤低质量知识）
        self.stopwords = {
            '你好', '谢谢', '再见', '欢迎', '请问', '？', '?',
            '好的', '收到', '明白', '了解了', '嗯', '哦', '啊',
            '是的', '对的', '没错', '对的', '这个', '那个'
        }

    def learn_from_text(
        self,
        text: str,
        conversation_id: str = None,
        user_role: str = "user"
    ) -> List[Dict[str, Any]]:
        """
        从文本中提取知识

        Args:
            text: 对话文本
            conversation_id: 对话ID（用于追踪来源）
            user_role: 说话者角色

        Returns:
            提取的知识单元列表
        """
        if not self.auto_learn:
            return []

        if not text or len(text.strip()) < self.config.get("learning", {}).get("min_content_length", 10):
            return []

        extracted = []

        # 1. 分割句子
        sentences = self._split_sentences(text)

        # 2. 分析每个句子
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue

            # 跳过常见的问候和问答
            if self._is_low_quality(sentence):
                continue

            # 提取知识
            knowledge = self._extract_knowledge(sentence, conversation_id, user_role)
            if knowledge:
                extracted.append(knowledge)

        # 3. 合并相关句子
        merged = self._merge_related_knowledge(extracted)

        # 4. 计算置信度
        for item in merged:
            item["confidence"] = self._calculate_confidence(item)

        return merged

    def _split_sentences(self, text: str) -> List[str]:
        """分割中文句子"""
        # 按句号、问号、感叹号和换行分割
        separators = r'[。！？.!?\n]'
        sentences = re.split(separators, text)

        # 过滤空字符串和过短的句子
        return [s.strip() for s in sentences if len(s.strip()) >= 5]

    def _is_low_quality(self, sentence: str) -> bool:
        """判断是否为低质量内容"""
        # 纯问题（以问号结尾或开头有疑问词）
        if sentence.endswith('?') or sentence.endswith('？'):
            return True

        # 问候语/常用语
        if sentence in self.stopwords:
            return True

        # 过短
        if len(sentence) < 10:
            return True

        # 仅表情符号
        if re.fullmatch(r'[\U00010000-\U0010ffff]+', sentence):
            return True

        # 大量重复字符
        if re.search(r'(.)\1{5,}', sentence):
            return True

        return False

    def _extract_knowledge(
        self,
        sentence: str,
        conversation_id: str,
        user_role: str
    ) -> Dict[str, Any]:
        """从句子中提取知识"""
        knowledge = {
            "content": sentence,
            "conversation_id": conversation_id,
            "user_role": user_role,
            "timestamp": datetime.now().isoformat(),
            "patterns_matched": [],
            "tags": []
        }

        # 提取专有名词（英文）
        english_terms = re.findall(self.ENGLISH_TERM_PATTERN, sentence)
        if english_terms:
            knowledge["tags"].extend(english_terms[:3])

        # 匹配定义模式
        for pattern in self.DEFINITION_PATTERNS:
            match = re.search(pattern, sentence)
            if match:
                term, definition = match.groups() if len(match.groups()) >= 2 else (match.group(1), "")
                knowledge["patterns_matched"].append("definition")
                knowledge["definition_term"] = term.strip()
                knowledge["content"] = f"{term}：{definition}"
                knowledge["tags"].append(self._normalize_tag(term))
                break

        # 匹配事实模式
        for pattern in self.FACT_PATTERNS:
            match = re.search(pattern, sentence)
            if match:
                knowledge["patterns_matched"].append("fact")
                # 提取可能的标签
                subject = match.group(1) if len(match.groups()) > 0 else ""
                if len(subject) <= 10:
                    knowledge["tags"].append(self._normalize_tag(subject))
                break

        return knowledge if knowledge["patterns_matched"] or english_terms else None

    def _normalize_tag(self, text: str) -> str:
        """标准化标签"""
        # 移除标点，提取关键词
        text = re.sub(r'[^\u4e00-\u9fff\w]', '', text)
        if len(text) <= 10:
            return text
        return text[:10]

    def _merge_related_knowledge(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并相关的知识单元"""
        if not items:
            return []

        merged = []
        used_indices = set()

        for i, item in enumerate(items):
            if i in used_indices:
                continue

            current = item.copy()
            related_indices = [i]

            # 查找相关的句子（相同模式或相同标签）
            for j, other in enumerate(items[i+1:], i+1):
                if j in used_indices:
                    continue

                # 判断是否相关
                is_related = (
                    set(current.get("patterns_matched", [])) & set(other.get("patterns_matched", []))
                    or set(current.get("tags", [])) & set(other.get("tags", []))
                    or self._similarity(current["content"], other["content"]) > 0.6
                )

                if is_related:
                    current["content"] += "；" + other["content"]
                    related_indices.append(j)
                    used_indices.add(j)

            # 标记相关对话
            current["source_conversations"] = list(set(
                [current["conversation_id"]] +
                [items[idx]["conversation_id"] for idx in related_indices]
            ))

            merged.append(current)
            used_indices.add(i)

        return merged

    def _similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的前缀匹配或包含关系
        if text1 in text2 or text2 in text1:
            return 0.8

        # 简单的字符重叠度
        set1 = set(text1)
        set2 = set(text2)
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _calculate_confidence(self, knowledge: Dict[str, Any]) -> float:
        """计算知识可信度"""
        confidence = 0.5  # 基础分

        # 匹配了模式加分
        if knowledge.get("patterns_matched"):
            confidence += 0.2 * len(knowledge["patterns_matched"])

        # 有标签加分
        if knowledge.get("tags"):
            confidence += 0.1

        # 内容长度加分（但不超过阈值）
        content_len = len(knowledge["content"])
        if 20 <= content_len <= 200:
            confidence += 0.1
        elif content_len > 200:
            confidence += 0.05

        # 来自用户（而不是助手的对话）加分
        if knowledge.get("user_role") == "user":
            confidence += 0.1

        # 限制在 0-1 范围
        return min(1.0, max(0.0, confidence))

    def analyze_conversation(
        self,
        conversation: List[Dict[str, Any]],
        conversation_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        分析完整对话

        Args:
            conversation: 对话列表，每个元素为 {"role": "user/assistant", "content": "内容"}
            conversation_id: 对话ID

        Returns:
            提取的所有知识单元
        """
        all_knowledge = []

        for message in conversation:
            role = message.get("role", "user")
            content = message.get("content", "")

            if not content:
                continue

            knowledge_items = self.learn_from_text(
                text=content,
                conversation_id=conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_role=role
            )

            all_knowledge.extend(knowledge_items)

        return all_knowledge


# 使用示例
if __name__ == "__main__":
    learner = ConversationLearner()

    # 模拟对话
    conversation = [
        {
            "role": "user",
            "content": "OpenClaw 是一个开源的智能体框架，用于构建自主 AI 助手。"
        },
        {
            "role": "assistant",
            "content": "了解到 OpenClaw 确实是一个智能体框架。它的主要特点包括模块化设计和可扩展的 Skill 系统。"
        },
        {
            "role": "user",
            "content": "对的。Skill 是 OpenClaw 的核心概念，每个 Skill 提供特定的功能，可以帮助智能体完成特定任务。"
        },
        {
            "role": "user",
            "content": "你好！请问今天天气怎么样？"
        }
    ]

    knowledge = learner.analyze_conversation(conversation)

    print(f"✓ 从对话中提取到 {len(knowledge)} 条知识：\n")
    for i, item in enumerate(knowledge, 1):
        print(f"[{i}] 置信度: {item['confidence']:.2f}")
        print(f"    内容: {item['content']}")
        print(f"    模式: {', '.join(item['patterns_matched'])}")
        print(f"    标签: {', '.join(item.get('tags', []))}")
        print()
