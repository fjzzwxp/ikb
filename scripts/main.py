#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续更新知识库技能 - 主入口

此技能用于：
1. 从文件中学习并提取知识
2. 从对话中持续学习和积累知识
3. 提供知识检索和查询功能
4. 管理和导出知识库
"""

import sys
import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

# 导入技能模块
from knowledge_base import KnowledgeBase, KnowledgeUnit
from file_processor import FileProcessor
from conversation_learner import ConversationLearner


class ContinuousKnowledgeBaseSkill:
    """持续更新知识库技能主类"""

    def __init__(self):
        """初始化技能"""
        self.config = self._load_config()
        self.kb = self._init_knowledge_base()
        self.file_processor = FileProcessor(self.config)
        self.conversation_learner = ConversationLearner(self.config)

        # 保存知识库文件的路径
        self.storage_path = self.config.get("knowledge_base", {}).get(
            "storage_path", "./knowledge/knowledge_db.json"
        )

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, '..', 'config', 'config.json')
        config_path = os.path.normpath(config_path)

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[INFO] 配置文件加载成功: {config_path}")
            return config
        except FileNotFoundError:
            print(f"[WARN] 配置文件未找到: {config_path}")
            print("[INFO] 使用默认配置")
            return {}
        except Exception as e:
            print(f"[ERROR] 配置文件加载失败: {e}")
            print("[INFO] 使用默认配置")
            return {}

    def _init_knowledge_base(self) -> KnowledgeBase:
        """初始化知识库"""
        storage_path = self.config.get("knowledge_base", {}).get(
            "storage_path", "./knowledge/knowledge_db.json"
        )

        script_dir = os.path.dirname(os.path.abspath(__file__))
        storage_path = os.path.join(script_dir, '..', storage_path)
        storage_path = os.path.normpath(storage_path)

        kb = KnowledgeBase(storage_path, self.config)
        return kb

    def parse_command(self, command: str) -> Dict[str, Any]:
        """
        解析用户命令

        支持的命令格式:
        1. 学习文件: "学习文件: [路径]" 或 "学习以下文件: path1, path2"
        2. 记录知识: "记录知识: [内容]" 或 "记录以下知识: 内容..."
        3. 搜索查询: "查询: [关键词]" 或 "搜索: 关键词"
        4. 查看统计: "统计" / "查看统计" / "知识库状态"
        5. 导出知识库: "导出为 [格式] 到 [路径]" 或 "导出 [格式]"
        """
        command = command.strip()

        # 学习文件
        if "学习文件" in command or "学习以下文件" in command:
            return self._parse_learn_files(command)

        # 记录知识
        elif "记录知识" in command or "记录以下知识" in command:
            return self._parse_record_knowledge(command)

        # 搜索
        elif "查询" in command or "搜索" in command or "查找" in command:
            return self._parse_search(command)

        # 统计
        elif "统计" in command or "状态" in command:
            return {"action": "stats"}

        # 导出
        elif "导出" in command:
            return self._parse_export(command)

        # 删除
        elif "删除" in command or "移除" in command:
            return self._parse_delete(command)

        # 获取详情
        elif "详情" in command or "查看" in command:
            return self._parse_view(command)

        else:
            return {"action": "unknown", "message": "无法识别的命令格式"}

    def _parse_learn_files(self, command: str) -> Dict[str, Any]:
        """解析学习文件命令"""
        # 提取文件路径
        paths = []

        # 提取冒号后的内容
        if ":" in command:
            paths_str = command.split(":", 1)[1].strip()
        elif "：" in command:
            paths_str = command.split("：", 1)[1].strip()
        else:
            # 查找列表格式
            lines = command.split('\n')
            paths_str = ' '.join([line.strip('- ') for line in lines if line.strip().startswith('-')])

        if not paths_str:
            return {"action": "error", "message": "请提供文件路径"}

        # 提取路径（支持空格分隔和列表）
        paths = re.findall(r'[^\s,，]+(?:\([^)]*\))?', paths_str)

        return {
            "action": "learn_files",
            "paths": [p.strip('"\'') for p in paths if p.strip()]
        }

    def _parse_record_knowledge(self, command: str) -> Dict[str, Any]:
        """解析记录知识命令"""
        # 提取知识内容
        if ":" in command:
            content = command.split(":", 1)[1].strip()
        elif "：" in command:
            content = command.split("：", 1)[1].strip()
        else:
            return {"action": "error", "message": "请提供知识内容"}

        # 提取标签（如果有）
        tags = []
        tag_match = re.search(r'标签为?[：:]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1)
            tags = [t.strip() for t in re.split(r'[,，、\s]+', tags_str) if t.strip()]
            content = re.sub(r'标签为?[：:]\s*.+$', '', content).strip()

        return {
            "action": "record",
            "content": content,
            "tags": tags,
            "confidence": 0.9
        }

    def _parse_search(self, command: str) -> Dict[str, Any]:
        """解析搜索命令"""
        # 提取关键词和结果数量
        query = ""
        max_results = self.config.get("search", {}).get("default_results", 5)

        # 提取关键词
        if ":" in command:
            parts = command.split(":", 1)[1].strip()
        elif "：" in command:
            parts = command.split("：", 1)[1].strip()
        else:
            parts = command

        # 提取返回数量
        number_match = re.search(r'返回\s*(\d+)\s*条', parts)
        if number_match:
            max_results = int(number_match.group(1))
            parts = re.sub(r'返回\s*\d+\s*条', '', parts).strip()

        query = parts.strip()

        return {
            "action": "search",
            "query": query,
            "max_results": max_results
        }

    def _parse_export(self, command: str) -> Dict[str, Any]:
        """解析导出命令"""
        format_match = re.search(r'导出(?:为|成)?\s*([a-zA-Z]+)', command)
        path_match = re.search(r'到\s*([^\s]+)', command) or re.search(r'保存到\s*([^\s]+)', command)

        export_format = format_match.group(1) if format_match else "json"
        output_path = path_match.group(1) if path_match else None

        return {
            "action": "export",
            "format": export_format.lower(),
            "output_path": output_path
        }

    def _parse_delete(self, command: str) -> Dict[str, Any]:
        """解析删除命令"""
        # 提取ID
        id_match = re.search(r'[：:]\s*([a-zA-Z0-9_\-]+)', command)
        if not id_match:
            return {"action": "error", "message": "请提供要删除的知识单元ID"}

        return {
            "action": "delete",
            "unit_id": id_match.group(1)
        }

    def _parse_view(self, command: str) -> Dict[str, Any]:
        """解析查看命令"""
        id_match = re.search(r'[：:]\s*([a-zA-Z0-9_\-]+)', command)

        if id_match:
            return {
                "action": "view",
                "unit_id": id_match.group(1)
            }
        else:
            return {"action": "view_all"}

    def run(self, command: str) -> str:
        """
        运行技能命令

        Returns:
            结果消息字符串
        """
        try:
            parsed = self.parse_command(command)
            action = parsed.get("action")

            if action == "error":
                return parsed.get("message", "命令解析失败")

            elif action == "unknown":
                return self._get_help()

            elif action == "learn_files":
                return self._handle_learn_files(parsed["paths"])

            elif action == "record":
                return self._handle_record(
                    parsed["content"],
                    parsed.get("tags", []),
                    parsed.get("confidence", 0.9)
                )

            elif action == "search":
                return self._handle_search(
                    parsed["query"],
                    parsed.get("max_results", 5)
                )

            elif action == "stats":
                return self._handle_stats()

            elif action == "export":
                return self._handle_export(
                    parsed["format"],
                    parsed.get("output_path")
                )

            elif action == "delete":
                return self._handle_delete(parsed["unit_id"])

            elif action == "view":
                return self._handle_view(parsed)

            else:
                return f"未知操作: {action}"

        except Exception as e:
            return f"❌ 执行失败: {str(e)}"

    def _handle_learn_files(self, file_paths: List[str]) -> str:
        """处理学习文件"""
        if not file_paths:
            return "请提供至少一个文件路径"

        results = []
        total_new = 0
        total_duplicate = 0

        for file_path in file_paths:
            try:
                # 处理文件
                units_data = self.file_processor.process_file(file_path)
                file_new = 0
                file_duplicate = 0

                for unit_data in units_data:
                    success, msg, _ = self.kb.add_knowledge(
                        content=unit_data["content"],
                        summary=unit_data.get("content", "")[:50],
                        tags=unit_data.get("tags", []),
                        source_type="file",
                        source_path=unit_data["source_path"],
                        context=unit_data.get("context", "")
                    )

                    if success:
                        file_new += 1
                    else:
                        file_duplicate += 1

                total_new += file_new
                total_duplicate += file_duplicate

                results.append(f"✓ {file_path}: 新增 {file_new}，重复 {file_duplicate}")

            except ImportError as e:
                results.append(f"⚠ {file_path}: 缺少依赖库 - {str(e)}")
            except Exception as e:
                results.append(f"✗ {file_path}: {str(e)}")

        summary = f"📊 处理完成：\n新增知识单元：{total_new}\n发现重复：{total_duplicate}\n总知识单元数：{len(self.kb.units)}\n\n"
        summary += "\n".join(results)

        return summary

    def _handle_record(self, content: str, tags: List[str], confidence: float) -> str:
        """处理记录知识"""
        success, msg, unit = self.kb.add_knowledge(
            content=content,
            tags=tags,
            source_type="manual",
            confidence=confidence
        )

        if success and unit:
            stats = self.kb.get_statistics()
            return (
                f"{msg}\n"
                f"📝 知识单元ID: {unit.id}\n"
                f"   摘要: {unit.summary}\n"
                f"   标签: {', '.join(unit.tags)}\n"
                f"   可信度: {unit.metadata['confidence']:.2f}\n"
                f"\n📊 当前知识库: {stats['total_units']} 个单元"
            )
        else:
            return msg

    def _handle_search(self, query: str, max_results: int) -> str:
        """处理搜索"""
        if not query:
            return "请输入搜索关键词"

        results = self.kb.search(query, max_results=max_results)

        if not results:
            return f"未找到与 '{query}' 相关的知识"

        output = f"🔍 搜索 '{query}' 的结果（找到 {len(results)} 条）：\n\n"

        for i, r in enumerate(results, 1):
            output += (
                f"[{i}] {r['summary']}\n"
                f"   ID: {r['id']} | 相关度: {r['relevance_score']:.2%}\n"
                f"   标签: {', '.join(r['tags'][:3])}\n"
                f"   来源: {r['source']['type']} | {r['source'].get('path', 'N/A')}\n"
                f"   内容: {r['content'][:100]}...\n\n"
            )

        return output

    def _handle_stats(self) -> str:
        """处理统计"""
        stats = self.kb.get_statistics()

        output = "📊 知识库统计信息\n"
        output += "=" * 40 + "\n\n"
        output += f"总知识单元：{stats['total_units']}\n\n"

        if stats['sources']:
            output += "来源分布：\n"
            for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
                percentage = count / stats['total_units'] * 100 if stats['total_units'] > 0 else 0
                output += f"  - {source}: {count} ({percentage:.1f}%)\n"

        if stats['tags']:
            output += "\n热门标签（Top 10）：\n"
            sorted_tags = sorted(
                stats['tags'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            for tag, count in sorted_tags:
                output += f"  #{tag}: {count}\n"

        if stats['recent_units']:
            output += f"\n最近更新：{stats['last_updated']}\n"
            output += "最近添加的单元：\n"
            for unit in stats['recent_units'][:5]:
                output += f"  - {unit['id']}: {unit['summary']} ({unit['source_type']})\n"

        return output

    def _handle_export(self, format: str, output_path: str = None) -> str:
        """处理导出"""
        success, msg = self.kb.export(format=format, output_path=output_path)
        return msg

    def _handle_delete(self, unit_id: str) -> str:
        """处理删除"""
        success, msg = self.kb.delete(unit_id)
        return msg

    def _handle_view(self, parsed: Dict[str, Any]) -> str:
        """处理查看"""
        unit_id = parsed.get("unit_id")

        if unit_id:
            unit = self.kb.get_by_id(unit_id)
            if not unit:
                return f"未找到ID为 {unit_id} 的知识单元"

            output = f"📄 知识单元详情\n"
            output += "=" * 40 + "\n\n"
            output += f"ID: {unit.id}\n"
            output += f"内容: {unit.content}\n\n"
            output += f"摘要: {unit.summary}\n"
            output += f"标签: {', '.join(unit.tags)}\n\n"
            output += f"来源:\n"
            output += f"  类型: {unit.source['type']}\n"
            output += f"  路径: {unit.source.get('path', 'N/A')}\n"
            output += f"  时间: {unit.source['timestamp']}\n"
            output += f"  上下文: {unit.source.get('context', '无')}\n\n"
            output += f"元数据:\n"
            output += f"  可信度: {unit.metadata['confidence']}\n"
            output += f"  字数: {unit.metadata['word_count']}\n"
            output += f"  语言: {unit.metadata['language']}\n"
            output += f"  版本: {unit.metadata['version']}\n"

            return output
        else:
            # 查看所有
            stats = self.kb.get_statistics()
            return self._handle_stats()

    def _get_help(self) -> str:
        """获取帮助信息"""
        help_text = """📚 持续知识库技能使用指南

【学习文件】
请使用 continuous-knowledge-base 技能学习文件: [文件路径]
支持格式：txt, md, json, csv, pdf, docx

【记录知识】
请使用 continuous-knowledge-base 技能记录知识: [内容]
你也可以指定标签: 标签为: 标签1, 标签2

【搜索查询】
请使用 continuous-knowledge-base 技能查询: [关键词]
可以指定返回数量: 请查询 项目计划 并返回 10 条结果

【查看统计】
请使用 continuous-knowledge-base 技能查看统计

【导出知识库】
请使用 continuous-knowledge-base 技能导出为 json 到 [文件路径]
支持格式：json, txt, csv

【查看/删除知识】
请使用 continuous-knowledge-base 技能查看: [知识单元ID]
请使用 continuous-knowledge-base 技能删除: [知识单元ID]

【示例命令】
- 学习文件: ./docs/readme.md
- 记录知识: OpenClaw 是一个智能体框架。标签为: OpenClaw, AI
- 查询: 项目计划
- 查看统计
- 导出为 json 到 ./backup.json
"""
        return help_text


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python main.py \"命令\"")
        print("示例: python main.py \"学习文件: ./test.txt\"")
        print("      python main.py \"查询: OpenClaw\"")
        print("      python main.py \"统计\"")
        print("\n使用 -h 或 --help 查看详细帮助")
        return

    # 处理帮助参数
    if sys.argv[1] in ['-h', '--help', 'help']:
        skill = ContinuousKnowledgeBaseSkill()
        print(skill._get_help())
        return

    # 运行技能
    command = " ".join(sys.argv[1:])
    skill = ContinuousKnowledgeBaseSkill()
    result = skill.run(command)
    print(result)


if __name__ == "__main__":
    main()
