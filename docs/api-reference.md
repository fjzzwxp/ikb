# API 参考文档

## KnowledgeBase 类

核心知识库类，提供知识的 CRUD 操作和检索功能。

### 初始化

```python
from knowledge_base import KnowledgeBase

kb = KnowledgeBase(
    storage_path="./knowledge/knowledge_db.json",
    config=config_dict
)
```

### 方法

#### `add_knowledge(...) -> Tuple[bool, str, KnowledgeUnit|None]`

添加新的知识单元。

**参数：**
- `content: str` - 知识内容（必需）
- `summary: str` - 简短摘要（可选，自动生成）
- `tags: List[str]` - 标签列表（可选，自动提取）
- `source_type: str` - 来源类型：file/conversation/manual
- `source_path: str` - 来源路径或ID
- `context: str` - 额外上下文信息
- `confidence: float` - 置信度（0-1）

**返回：**
- `(是否新增, 消息, 知识单元对象)`

**示例：**
```python
success, msg, unit = kb.add_knowledge(
    content="OpenClaw 使用 Skill 系统进行功能扩展",
    source_type="manual",
    confidence=0.9
)
```

#### `search(query: str, max_results: int = 5, min_similarity: float = 0.3) -> List[Dict]`

搜索知识库。

**参数：**
- `query: str` - 搜索关键词
- `max_results: int` - 最大返回结果数
- `min_similarity: float` - 最小相似度阈值（0-1）

**返回：** 按相关度排序的结果列表

**示例：**
```python
results = kb.search("OpenClaw Skill系统", max_results=10)
for r in results:
    print(f"{r['summary']} (相关度: {r['relevance_score']:.2%})")
```

#### `get_statistics() -> Dict[str, Any]`

获取知识库统计信息。

**返回：**
```json
{
  "total_units": 156,
  "sources": {"file": 120, "conversation": 30, "manual": 6},
  "tags": {"OpenClaw": 15, "Skill": 12, ...},
  "recent_units": [...],
  "last_updated": "2026-05-15T13:20:00"
}
```

#### `get_by_id(unit_id: str) -> KnowledgeUnit|None`

根据ID获取知识单元。

#### `delete(unit_id: str) -> Tuple[bool, str]`

删除知识单元。

#### `export(format: str = "json", output_path: str = None) -> Tuple[bool, str]`

导出知识库。

**支持格式：** json, txt, csv

**示例：**
```python
success, msg = kb.export(format="txt", output_path="./backup/kb_export.txt")
```

---

## FileProcessor 类

文件处理器，支持多种格式的知识提取。

### 初始化

```python
from file_processor import FileProcessor

processor = FileProcessor(config)
```

### 方法

#### `can_process(file_path: str) -> Tuple[bool, str]`

检查文件是否可以处理。

#### `process_file(file_path: str) -> List[Dict]`

处理文件并提取知识单元。

**返回：** 知识单元列表，每个元素包含：
- `content: str` - 内容
- `source_path: str` - 源文件路径
- `context: str` - 上下文（如"第X行数据"）
- `tags: List[str]` - 标签

**示例：**
```python
units = processor.process_file("./docs/project.md")
print(f"提取了 {len(units)} 个知识单元")
```

---

## ConversationLearner 类

对话学习器，从对话中自动提取知识。

### 初始化

```python
from conversation_learner import ConversationLearner

learner = ConversationLearner(config)
```

### 方法

#### `learn_from_text(text: str, conversation_id: str, user_role: str) -> List[Dict]`

从单条文本中提取知识。

**参数：**
- `text: str` - 对话文本
- `conversation_id: str` - 对话ID（用于来源追踪）
- `user_role: str` - 说话者角色（user/assistant）

**返回：** 知识单元列表

#### `analyze_conversation(conversation: List[Dict], conversation_id: str|None) -> List[Dict]`

分析完整对话。

**参数：**
- `conversation: List[Dict]` - 对话列表，每个元素格式：
  ```python
  {
    "role": "user"|"assistant",
    "content": "对话内容"
  }
  ```
- `conversation_id: str` - 对话ID（可选）

**示例：**
```python
conv = [
    {"role": "user", "content": "OpenClaw 是一个智能体框架。"},
    {"role": "assistant", "content": "我知道了。OpenClaw确实是一个智能体框架。"}
]

knowledge = learner.analyze_conversation(conv)
for k in knowledge:
    print(f"提取: {k['content']} (置信度: {k['confidence']:.2f})")
```

---

## 配置文件结构

```json
{
  "knowledge_base": {
    "storage_path": "./knowledge/knowledge_db.json",
    "vector_enabled": false,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "similarity_threshold": 0.85,
    "max_file_size_mb": 10,
    "supported_extensions": [".txt", ".md", ".json", ".csv", ".pdf", ".docx"]
  },
  "learning": {
    "auto_learn_from_conversation": true,
    "confidence_threshold": 0.7,
    "min_content_length": 10,
    "max_knowledge_units_per_file": 100,
    "extract_conversation_patterns": true
  },
  "search": {
    "default_results": 5,
    "max_results": 20,
    "semantic_search": false,
    "min_similarity_score": 0.3
  }
}
```

---

## 知识单元 JSON 结构

```json
{
  "id": "abc123def",
  "content": "知识的具体内容",
  "summary": "简短摘要",
  "tags": ["标签1", "标签2"],
  "source": {
    "type": "file",
    "path": "./docs/README.md",
    "timestamp": "2026-05-15T13:30:00.123456",
    "context": "自动分割-第3段"
  },
  "metadata": {
    "confidence": 0.95,
    "word_count": 45,
    "language": "zh-CN",
    "version": 1,
    "related_ids": ["xyz789"]
  }
}
```

---

## 异常处理

所有操作都可能抛出异常，建议捕获：

```python
try:
    kb.add_knowledge(content=text)
except ImportError as e:
    print(f"缺少依赖: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 性能建议

1. **大量文件处理**：分批处理，每个批次后保存
2. **频繁搜索**：考虑启用向量搜索（需额外依赖）
3. **大文件**：调整 `max_knowledge_units_per_file` 限制
4. **去重精度**：调整 `similarity_threshold`（默认 0.85）
