#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库核心模块
提供知识的存储、检索、更新和管理功能
"""

import json
import os
import uuid
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher


class KnowledgeUnit:
    """单个知识单元类"""

    def __init__(
        self,
        content: str,
        summary: str = None,
        tags: List[str] = None,
        source_type: str = "manual",
        source_path: str = None,
        context: str = None,
        confidence: float = 1.0,
        related_ids: List[str] = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.content = content.strip()
        self.summary = summary or self._generate_summary()
        self.tags = tags or self._extract_tags()
        self.source = {
            "type": source_type,
            "path": source_path,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        self.metadata = {
            "confidence": confidence,
            "word_count": len(self.content),
            "language": self._detect_language(),
            "version": 1,
            "related_ids": related_ids or []
        }

    def _generate_summary(self) -> str:
        """生成简短摘要"""
        if len(self.content) <= 50:
            return self.content
        return self.content[:50] + "..."

    def _extract_tags(self) -> List[str]:
        """从内容中提取关键词作为标签"""
        # 简单的中文分词和关键词提取
        # 移除停用词
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就',
                    '不', '人', '都', '一', '一个', '上', '也', '很',
                    '到', '说', '要', '去', '你', '会', '着', '没有',
                    '看', '好', '自己', '这', '那', '她', '他', '它'}

        # 提取中文字符和英文单词
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', self.content)
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', self.content)

        # 统计词频
        word_freq = {}
        for chars in chinese_chars:
            if len(chars) >= 2 and chars not in stopwords:
                word_freq[chars] = word_freq.get(chars, 0) + 1

        for word in english_words:
            word_lower = word.lower()
            if word_lower not in stopwords:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1

        # 取前5个最频繁的词作为标签
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, freq in sorted_words[:5]]

        return tags if tags else ["未分类"]

    def _detect_language(self) -> str:
        """简单检测语言"""
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', self.content))
        english_count = len(re.findall(r'[a-zA-Z]', self.content))

        if chinese_count > english_count:
            return "zh-CN"
        elif english_count > 0:
            return "en"
        return "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "summary": self.summary,
            "tags": self.tags,
            "source": self.source,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeUnit':
        """从字典创建知识单元"""
        unit = cls(
            content=data["content"],
            summary=data.get("summary"),
            tags=data.get("tags"),
            source_type=data["source"]["type"],
            source_path=data["source"].get("path"),
            context=data["source"].get("context"),
            confidence=data["metadata"]["confidence"],
            related_ids=data["metadata"].get("related_ids", [])
        )
        unit.id = data["id"]
        # 恢复时间戳
        unit.source["timestamp"] = data["source"]["timestamp"]
        return unit


class KnowledgeBase:
    """知识库核心类"""

    def __init__(self, storage_path: str, config: Dict[str, Any] = None):
        self.storage_path = storage_path
        self.config = config or {}
        self.units: Dict[str, KnowledgeUnit] = {}
        self.embeddings_cache = {}

        # 加载配置
        self.similarity_threshold = self.config.get(
            "knowledge_base", {}).get("similarity_threshold", 0.85)
        self.vector_enabled = self.config.get(
            "knowledge_base", {}).get("vector_enabled", False)

        # 加载知识库
        self.load()

        # 如果启用向量搜索，初始化 embedding 模型
        if self.vector_enabled:
            self._init_embedding_model()

    def _init_embedding_model(self):
        """初始化 embedding 模型（可选功能）"""
        try:
            # from sentence_transformers import SentenceTransformer
            # self.embedding_model = SentenceTransformer(
            #     self.config.get("knowledge_base", {}).get(
            #         "embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            # )
            print("注意：向量搜索功能需要安装 sentence-transformers 库")
            print("请运行: pip install sentence-transformers")
            self.vector_enabled = False
        except ImportError:
            print("警告：sentence-transformers 未安装，将使用基于文本的相似度计算")
            self.vector_enabled = False

    def load(self) -> bool:
        """从文件加载知识库"""
        if not os.path.exists(self.storage_path):
            print(f"知识库文件不存在，将创建新的: {self.storage_path}")
            self.units = {}
            return True

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.units = {}
            for unit_data in data.get("knowledge_units", []):
                unit = KnowledgeUnit.from_dict(unit_data)
                self.units[unit.id] = unit

            print(f"✓ 知识库加载成功: {len(self.units)} 个知识单元")
            return True
        except Exception as e:
            print(f"✗ 知识库加载失败: {e}")
            self.units = {}
            return False

    def save(self) -> bool:
        """保存知识库到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

            data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat() if not self.units else list(self.units.values())[0].source["timestamp"],
                "last_updated": datetime.now().isoformat(),
                "total_units": len(self.units),
                "sources": self._get_source_statistics(),
                "knowledge_units": [unit.to_dict() for unit in self.units.values()],
                "embeddings": {
                    "enabled": self.vector_enabled,
                    "model": self.config.get("knowledge_base", {}).get("embedding_model")
                } if self.vector_enabled else {"enabled": False}
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"✗ 知识库保存失败: {e}")
            return False

    def _get_source_statistics(self) -> Dict[str, int]:
        """获取来源统计"""
        stats = {}
        for unit in self.units.values():
            source_type = unit.source["type"]
            stats[source_type] = stats.get(source_type, 0) + 1
        return stats

    def add_knowledge(
        self,
        content: str,
        summary: str = None,
        tags: List[str] = None,
        source_type: str = "manual",
        source_path: str = None,
        context: str = None,
        confidence: float = 1.0
    ) -> Tuple[bool, str, Optional[KnowledgeUnit]]:
        """
        添加知识单元

        Returns:
            (是否新增, 消息, 知识单元对象)
        """
        if not content or len(content.strip()) < self.config.get("learning", {}).get("min_content_length", 10):
            return False, "内容太短，无法添加", None

        # 检查是否与现有知识重复
        is_duplicate, similar_unit, similarity = self._find_similar(content)
        if is_duplicate:
            msg = f"知识已存在（相似度: {similarity:.2%}）: {similar_unit.summary}"
            return False, msg, similar_unit

        # 创建新知识单元
        unit = KnowledgeUnit(
            content=content,
            summary=summary,
            tags=tags,
            source_type=source_type,
            source_path=source_path,
            context=context,
            confidence=confidence
        )

        # 添加到知识库
        self.units[unit.id] = unit

        # 保存到文件
        if self.save():
            return True, f"✅ 知识已添加 (ID: {unit.id})", unit
        else:
            return False, "❌ 保存失败", None

    def _find_similar(self, content: str) -> Tuple[bool, Optional[KnowledgeUnit], float]:
        """查找相似的知识"""
        if not self.units:
            return False, None, 0.0

        best_similarity = 0.0
        best_unit = None

        for unit in self.units.values():
            similarity = self._calculate_similarity(content, unit.content)
            if similarity > best_similarity:
                best_similarity = similarity
                best_unit = unit

        if best_similarity >= self.similarity_threshold:
            return True, best_unit, best_similarity

        return False, None, best_similarity

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        # 使用编辑距离比率的简单方法
        # 对于短文本效果较好
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def search(
        self,
        query: str,
        max_results: int = None,
        min_similarity: float = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识

        Returns:
            按相关性排序的结果列表
        """
        max_results = max_results or self.config.get("search", {}).get("default_results", 5)
        min_similarity = min_similarity or self.config.get("search", {}).get("min_similarity_score", 0.1)

        if not query or not self.units:
            return []

        query_lower = query.lower()
        results = []
        for unit in self.units.values():
            # 计算内容相似度
            content_similarity = self._calculate_similarity(query, unit.content)

            # 关键词直接匹配（包含检查）
            keyword_match = query_lower in unit.content.lower() or query_lower in unit.summary.lower()
            keyword_score = 0.5 if keyword_match else 0

            # 计算标签匹配度
            tag_match = any(query_lower in tag.lower() for tag in unit.tags)
            tag_score = 0.3 if tag_match else 0

            # 计算摘要相似度
            summary_similarity = self._calculate_similarity(query, unit.summary) if unit.summary else 0

            # 综合得分（可调整权重）
            total_score = (
                keyword_score * 0.4 +
                content_similarity * 0.3 +
                tag_score * 0.2 +
                summary_similarity * 0.1
            )

            if total_score >= min_similarity:
                result = unit.to_dict()
                result["relevance_score"] = round(total_score, 4)
                results.append(result)

        # 按相关度排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results[:max_results]

    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if not self.units:
            return {
                "total_units": 0,
                "sources": {},
                "tags": {},
                "recent_units": []
            }

        # 统计来源
        sources = self._get_source_statistics()

        # 统计标签
        tag_stats = {}
        for unit in self.units.values():
            for tag in unit.tags:
                tag_stats[tag] = tag_stats.get(tag, 0) + 1

        # 获取最近添加的5个单元
        sorted_units = sorted(
            self.units.values(),
            key=lambda x: x.source["timestamp"],
            reverse=True
        )
        recent_units = [
            {
                "id": unit.id,
                "summary": unit.summary,
                "source_type": unit.source["type"],
                "timestamp": unit.source["timestamp"]
            }
            for unit in sorted_units[:5]
        ]

        return {
            "total_units": len(self.units),
            "sources": sources,
            "tags": tag_stats,
            "recent_units": recent_units,
            "last_updated": sorted_units[0].source["timestamp"] if sorted_units else None
        }

    def get_by_id(self, unit_id: str) -> Optional[KnowledgeUnit]:
        """根据ID获取知识单元"""
        return self.units.get(unit_id)

    def delete(self, unit_id: str) -> Tuple[bool, str]:
        """删除知识单元"""
        if unit_id not in self.units:
            return False, f"知识单元 {unit_id} 不存在"

        unit = self.units[unit_id]
        del self.units[unit_id]

        if self.save():
            return True, f"✅ 知识单元 {unit_id} 已删除: {unit.summary}"
        else:
            return False, f"❌ 删除失败"

    def export(
        self,
        format: str = "json",
        output_path: str = None
    ) -> Tuple[bool, str]:
        """
        导出知识库

        Args:
            format: 导出格式（json, txt, csv）
            output_path: 输出文件路径
        """
        if not self.units:
            return False, "知识库为空，无法导出"

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./knowledge/export_{timestamp}.{format}"

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format.lower() == "json":
                data = {
                    "version": "1.0",
                    "export_time": datetime.now().isoformat(),
                    "total_units": len(self.units),
                    "knowledge_units": [unit.to_dict() for unit in self.units.values()]
                }
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif format.lower() == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"知识库导出\n")
                    f.write(f"导出时间: {datetime.now().isoformat()}\n")
                    f.write(f"总单元数: {len(self.units)}\n")
                    f.write("=" * 80 + "\n\n")

                    for i, unit in enumerate(self.units.values(), 1):
                        f.write(f"[{i}] ID: {unit.id}\n")
                        f.write(f"标签: {', '.join(unit.tags)}\n")
                        f.write(f"来源: {unit.source['type']} | {unit.source.get('path', 'N/A')}\n")
                        f.write(f"时间: {unit.source['timestamp']}\n")
                        f.write(f"可信度: {unit.metadata['confidence']}\n")
                        f.write("-" * 40 + "\n")
                        f.write(f"{unit.content}\n")
                        f.write("=" * 80 + "\n\n")

            elif format.lower() == "csv":
                import csv
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '内容', '摘要', '标签', '来源类型', '来源路径', '时间戳', '可信度', '字数'])
                    for unit in self.units.values():
                        writer.writerow([
                            unit.id,
                            unit.content,
                            unit.summary,
                            ';'.join(unit.tags),
                            unit.source['type'],
                            unit.source.get('path', ''),
                            unit.source['timestamp'],
                            unit.metadata['confidence'],
                            unit.metadata['word_count']
                        ])
            else:
                return False, f"不支持的导出格式: {format}"

            return True, f"✅ 知识库已导出到: {output_path}"

        except Exception as e:
            return False, f"❌ 导出失败: {e}"


# 使用示例
if __name__ == "__main__":
    # 加载配置
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'config',
        'config.json'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {}

    # 创建知识库
    storage_path = config.get("knowledge_base", {}).get(
        "storage_path", "./knowledge/knowledge_db.json"
    )
    kb = KnowledgeBase(storage_path, config)

    # 添加测试知识
    success, msg, unit = kb.add_knowledge(
        content="OpenClaw 是一个智能体系统，支持通过 Skill 扩展功能。",
        source_type="manual",
        confidence=0.9
    )
    print(msg)

    # 搜索
    results = kb.search("OpenClaw 智能体")
    print(f"\n搜索到 {len(results)} 条结果:")
    for r in results:
        print(f"  - {r['summary']} (相关度: {r['relevance_score']:.2%})")

    # 查看统计
    stats = kb.get_statistics()
    print(f"\n统计: {stats['total_units']} 个单元，{len(stats['tags'])} 个标签")
