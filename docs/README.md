# 持续更新知识库技能

这是一个为 OpenClaw 智能体设计的持续学习知识库技能。

## 功能特性

- 📚 从多种文件格式中学习（txt, md, json, pdf, docx, csv）
- 💬 从对话中自动提取知识
- 🔍 智能搜索和知识检索
- 🔄 自动去重和更新机制
- 📊 知识库统计和可视化
- 💾 多格式导出（json, txt, csv）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

可选依赖（用于处理 PDF 和 DOCX）：
```bash
pip install pdfplumber python-docx
```

### 2. 学习文件

```bash
python scripts/main.py "学习文件: ./docs/project-overview.md"
```

### 3. 查询知识

```bash
python scripts/main.py "查询: 项目目标"
```

### 4. 查看统计

```bash
python scripts/main.py "统计"
```

## 目录结构

```
continuous-knowledge-base/
├── SKILL.md              # 技能说明文档
├── config/
│   └── config.json       # 配置文件
├── scripts/
│   ├── main.py           # 主入口
│   ├── knowledge_base.py  # 知识库核心
│   ├── file_processor.py # 文件处理器
│   └── conversation_learner.py  # 对话学习器
├── knowledge/
│   └── knowledge_db.json # 知识库存储文件
└── docs/
    ├── README.md
    ├── project-overview.md
    ├── technical-stack.md
    └── api-reference.md
```

## 使用示例

### 学习多个文件

```bash
python scripts/main.py "学习文件: ./docs/README.md ./docs/TECH-STACK.md"
```

### 记录一条新知识

```bash
python scripts/main.py "记录知识: 项目采用微服务架构，包括用户服务、订单服务和支付服务。 标签为: 架构, 微服务"
```

### 搜索并限制结果数

```bash
python scripts/main.py "查询: 微服务 并返回 10 条结果"
```

### 导出知识库

```bash
python scripts/main.py "导出为 txt 到 ./backup/knowledge_export.txt"
```

## 配置说明

编辑 `config/config.json` 可以调整：

- `knowledge_base.storage_path`: 知识库存储路径
- `knowledge_base.similarity_threshold`: 相似度阈值（0-1），越低越容易识别为重复
- `learning.confidence_threshold`: 对话学习的置信度阈值
- `search.default_results`: 默认返回结果数量

## 知识库结构

知识库以 JSON 格式存储，包含：

- 知识单元（内容、摘要、标签、来源、元数据）
- 版本信息和统计

每个知识单元都有唯一的 ID，并且记录了来源和时间戳。

## 从对话中学习

本技能可以集成到 OpenClaw 的对话流程中，自动从用户对话中提取知识：

```python
# 在对话处理逻辑中
conversation = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
]

learner = ConversationLearner(config)
knowledge = learner.analyze_conversation(conversation)

for item in knowledge:
    kb.add_knowledge(
        content=item["content"],
        source_type="conversation",
        confidence=item["confidence"]
    )
```

## 注意事项

1. **文件大小限制**：默认单个文件最大 10MB
2. **去重机制**：基于内容相似度自动避免重复
3. **向量搜索**：可选功能，需要安装 sentence-transformers
4. **定期维护**：建议定期审查和清理知识库

## 扩展开发

- 添加新的文件格式支持：在 `FileProcessor.SUPPORTED_EXTENSIONS` 中添加
- 改进相似度计算：修改 `KnowledgeBase._calculate_similarity()` 方法
- 自定义标签提取：修改 `KnowledgeUnit._extract_tags()` 方法
- 启用向量搜索：修改配置文件，安装 sentence-transformers

## 故障排除

**问题：PDF 文件无法处理**
```bash
pip install pdfplumber
```

**问题：DOCX 文件无法处理**
```bash
pip install python-docx
```

**问题：查询结果不相关**
- 调整配置文件中的 `similarity_threshold`（值越低压根越容易匹配）
- 确保知识库中有相关标签

**问题：知识重复**
- 提高 `similarity_threshold`（例如 0.90）

## License

MIT
