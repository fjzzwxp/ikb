#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理器模块
支持多种文件格式的知识提取
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path


class FileProcessor:
    """文件处理器类"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {
        '.txt': '_process_text',
        '.md': '_process_markdown',
        '.json': '_process_json',
        '.csv': '_process_csv',
        '.pdf': '_process_pdf',
        '.docx': '_process_docx'
    }

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_file_size = self.config.get(
            "knowledge_base", {}).get("max_file_size_mb", 10) * 1024 * 1024
        self.supported_exts = self.config.get(
            "knowledge_base", {}).get("supported_extensions", list(self.SUPPORTED_EXTENSIONS.keys())
        )
        self.max_units = self.config.get(
            "learning", {}).get("max_knowledge_units_per_file", 100)

    def can_process(self, file_path: str) -> Tuple[bool, str]:
        """检查文件是否可以处理"""
        path = Path(file_path)

        if not path.exists():
            return False, "文件不存在"

        if not path.is_file():
            return False, "路径不是文件"

        ext = path.suffix.lower()
        if ext not in self.supported_exts:
            return False, f"不支持的文件格式: {ext}"

        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            return False, f"文件太大: {file_size/1024/1024:.1f}MB (最大 {self.max_file_size/1024/1024}MB)"

        return True, "OK"

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        处理文件，提取知识单元

        Returns:
            知识单元列表
        """
        can_process, msg = self.can_process(file_path)
        if not can_process:
            raise ValueError(f"无法处理文件: {msg}")

        ext = Path(file_path).suffix.lower()
        method_name = self.SUPPORTED_EXTENSIONS.get(ext)

        if not method_name:
            raise ValueError(f"不支持的文件格式: {ext}")

        method = getattr(self, method_name)
        return method(file_path)

    def _process_text(self, file_path: str) -> List[Dict[str, Any]]:
        """处理纯文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self._split_into_units(content, file_path, "text")

    def _process_markdown(self, file_path: str) -> List[Dict[str, Any]]:
        """处理 Markdown 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 移除 Markdown 标记
        # 移除标题标记 (#)
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        # 移除粗体/斜体标记
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        # 移除链接 [text](url)
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
        # 移除图片
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        # 移除代码块
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        # 移除行内代码
        content = re.sub(r'`(.*?)`', r'\1', content)

        return self._split_into_units(content, file_path, "markdown")

    def _process_json(self, file_path: str) -> List[Dict[str, Any]]:
        """处理 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        units = []

        def extract_from_obj(obj, path=""):
            """递归提取内容"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        extract_from_obj(value, new_path)
                    elif isinstance(value, str) and len(value.strip()) >= 10:
                        units.append({
                            "content": value.strip(),
                            "source_path": file_path,
                            "context": f"字段: {new_path}",
                            "tags": [key]
                        })
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    extract_from_obj(item, new_path)
            elif isinstance(obj, str) and len(obj.strip()) >= 10:
                units.append({
                    "content": obj.strip(),
                    "source_path": file_path,
                    "context": f"路径: {path}",
                    "tags": ["文本数据"]
                })

        extract_from_obj(data)

        # 如果没有提取到单元，则整个文件作为一条知识
        if not units:
            units.append({
                "content": json.dumps(data, ensure_ascii=False, indent=2),
                "source_path": file_path,
                "context": "完整JSON文件",
                "tags": ["JSON"]
            })

        return units

    def _process_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """处理 CSV 文件"""
        import csv

        units = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if not rows:
                return []

            # 获取列名
            headers = reader.fieldnames or []

            # 为每行数据创建知识单元
            for i, row in enumerate(rows[:min(50, len(rows))]):  # 限制处理行数
                content_parts = []
                for header in headers:
                    value = row.get(header, "").strip()
                    if value:
                        content_parts.append(f"{header}: {value}")

                if content_parts:
                    units.append({
                        "content": " | ".join(content_parts),
                        "source_path": file_path,
                        "context": f"第 {i+1} 行数据",
                        "tags": headers[:3] if len(headers) > 3 else headers
                    })

        return units

    def _process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """处理 PDF 文件（需要安装 PyPDF2 或 pdfplumber）"""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "处理 PDF 需要安装 pdfplumber。请运行: pip install pdfplumber"
            )

        units = []

        with pdfplumber.open(file_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        if not full_text.strip():
            raise ValueError("PDF 文件未提取到文本内容")

        return self._split_into_units(full_text, file_path, "pdf")

    def _process_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """处理 DOCX 文件（需要安装 python-docx）"""
        try:
            import docx
        except ImportError:
            raise ImportError(
                "处理 DOCX 需要安装 python-docx。请运行: pip install python-docx"
            )

        doc = docx.Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])

        if not content.strip():
            raise ValueError("DOCX 文件未提取到文本内容")

        return self._split_into_units(content, file_path, "docx")

    def _split_into_units(
        self,
        content: str,
        file_path: str,
        source_type: str
    ) -> List[Dict[str, Any]]:
        """
        将内容分割成知识单元

        策略：
        1. 按段落分割（双换行）
        2. 按句子分割（句号、问号、感叹号）
        3. 限制每个单元的长度
        """
        content = content.strip()
        if not content:
            return []

        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        units = []
        current_unit = []
        current_length = 0

        # 最小单元长度（字符数）
        min_length = 50
        # 最大单元长度
        max_length = 500

        for para in paragraphs:
            para_length = len(para)

            # 如果段落本身很长，进一步分割
            if para_length > max_length * 1.5:
                # 按句子分割
                sentences = re.split(r'[。！？.!?;；\n]+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if len(current_unit) == 0 or current_length + len(sentence) <= max_length:
                        current_unit.append(sentence)
                        current_length += len(sentence)
                    else:
                        # 保存当前单元
                        if current_length >= min_length:
                            units.append({
                                "content": " ".join(current_unit),
                                "source_path": file_path,
                                "context": "自动分割",
                                "tags": []
                            })
                        current_unit = [sentence]
                        current_length = len(sentence)
            else:
                # 普通段落
                if current_length + para_length <= max_length:
                    current_unit.append(para)
                    current_length += para_length
                else:
                    # 保存当前单元
                    if current_length >= min_length:
                        units.append({
                            "content": " ".join(current_unit),
                            "source_path": file_path,
                            "context": "自动分割",
                            "tags": []
                        })
                    current_unit = [para]
                    current_length = para_length

        # 保存最后一个单元
        if current_length >= min_length:
            units.append({
                "content": " ".join(current_unit),
                "source_path": file_path,
                "context": "自动分割",
                "tags": []
            })

        # 限制单元数量
        if len(units) > self.max_units:
            print(f"⚠ 文件分割出 {len(units)} 个单元，超过限制 {self.max_units}，将截断")
            units = units[:self.max_units]

        return units


# 使用示例
if __name__ == "__main__":
    processor = FileProcessor()

    # 测试处理文本文件
    test_file = "./test.txt"

    if os.path.exists(test_file):
        try:
            units = processor.process_file(test_file)
            print(f"✓ 处理完成，提取 {len(units)} 个知识单元")
            for i, unit in enumerate(units[:3], 1):
                print(f"\n[{i}] {unit['content'][:100]}...")
        except Exception as e:
            print(f"✗ 处理失败: {e}")
    else:
        print(f"测试文件不存在: {test_file}")
        print("请创建一个测试文件，例如：")
        print("""
这是一个测试文件。

它包含多个段落。

这是第三个段落，包含了更多信息。
        """)
