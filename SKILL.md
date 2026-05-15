---
name: "continuous-knowledge-base"
description: "管理一个持续更新的知识库，可以从文件和对话中学习新知识。当用户需要添加文件、更新知识库或查询信息时调用此技能。"
author: SKILL Developer
version: 1.0.0
tags: [knowledge-base, learning, file-processing, continuous-update]
---

# 持续更新知识库技能

## 技能用途

此技能用于创建一个不断学习和更新的知识库系统，主要功能包括：

1. **文件学习**：从用户提供的文件中提取知识（支持 txt、md、json、pdf 等格式）
2. **对话学习**：从与用户的对话中识别并存储有价值的新知识
3. **知识检索**：根据查询关键词在知识库中搜索相关信息
4. **知识更新**：支持增量更新，自动检测并处理重复或过时的知识
5. **知识导出**：可将知识库导出为不同格式

## 使用方法

### 添加文件到知识库

```
请使用 continuous-knowledge-base 技能学习文件：[文件路径]
```

或批量学习：

```
请使用 continuous-knowledge-base 技能学习以下文件：
- 文件1.txt
- 文件2.pdf
- 文件3.json
```

### 从对话中学习

```
请使用 continuous-knowledge-base 技能记录以下知识：[新知识内容]
```

### 查询知识库

```
请使用 continuous-knowledge-base 技能查询：[查询关键词]
```

或详细查询：

```
请使用 continuous-knowledge-base 技能查询：[关键词]，返回 [数量] 条最相关结果
```

### 查看知识库状态

```
请使用 continuous-knowledge-base 技能查看统计信息
```

### 导出知识库

```
请使用 continuous-knowledge-base 技能导出知识库：[格式] 到 [文件路径]
```

## 功能流程

### 1. 文件处理流程

1. **文件读取**：支持多种文件格式（txt、md、json、pdf、docx）
2. **内容提取**：根据文件类型使用适当的解析器提取文本内容
3. **知识分割**：将长文本分割成适合存储的知识单元
4. **知识摘要**：为每个知识单元生成简洁的摘要和标签
5. **重复检测**：与现有知识对比，避免重复存储
6. **知识存储**：将新知识存入知识库

### 2. 对话学习流程

1. **内容分析**：识别对话中的关键信息和新知识
2. **知识提取**：提取有价值的陈述、事实、定义等
3. **上下文关联**：记录知识的来源对话和上下文
4. **可信度评估**：根据来源和内容评估知识可信度
5. **知识存储**：将处理后的知识存入知识库

### 3. 查询流程

1. **查询解析**：理解用户的查询意图
2. **关键词提取**：提取核心搜索关键词
3. **语义搜索**：计算查询与知识库内容的相似度
4. **结果排序**：按相关性对结果进行排序
5. **结果格式化**：返回格式化的结果列表

### 4. 更新机制

- **增量学习**：新知识不会覆盖旧知识，而是补充
- **去重策略**：基于内容相似度检测重复知识
- **版本控制**：同一主题的不同观点可以并存，并记录时间戳
- **过期管理**：可标记可能过时的知识，供人工审核

## 配置说明

在 `config/config.json` 中配置知识库参数：

```json
{
  "knowledge_base": {
    "storage_path": "./knowledge/knowledge_db.json",
    "vector_enabled": false,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "similarity_threshold": 0.85,
    "max_file_size_mb": 10,
    "supported_extensions": [".txt", ".md", ".json", ".pdf", ".docx"]
  },
  "learning": {
    "auto_learn_from_conversation": true,
    "confidence_threshold": 0.7,
    "min_content_length": 10,
    "max_knowledge_units_per_file": 100
  },
  "search": {
    "default_results": 5,
    "max_results": 20,
    "semantic_search": true
  }
}
```

## 数据结构

### 知识单元结构

```json
{
  "id": "uuid",
  "content": "知识内容",
  "summary": "简洁摘要",
  "tags": ["标签1", "标签2"],
  "source": {
    "type": "file|conversation|manual",
    "path": "文件路径或对话ID",
    "timestamp": "2026-05-15T13:30:00",
    "context": "额外上下文信息"
  },
  "metadata": {
    "confidence": 0.95,
    "word_count": 150,
    "language": "zh-CN",
    "version": 1,
    "related_ids": ["相关知识的ID"]
  }
}
```

### 知识库结构

```json
{
  "version": "1.0",
  "created_at": "2026-05-15T13:00:00",
  "last_updated": "2026-05-15T13:30:00",
  "total_units": 156,
  "sources": {
    "file": 120,
    "conversation": 30,
    "manual": 6
  },
  "knowledge_units": [
    { ... }
  ],
  "embeddings": {
    "enabled": false,
    "model": null
  }
}
```

## 注意事项

1. **文件大小**：默认限制单个文件最大 10MB
2. **内容质量**：过于短小的内容可能被自动过滤
3. **重复检测**：使用余弦相似度，阈值默认 0.85
4. **性能考虑**：大型知识库建议启用向量搜索以提高查询效率
5. **隐私安全**：知识库存储在本地，确保敏感信息不会外泄
6. **定期清理**：建议定期审查知识库内容，移除过期或不准确的信息

## 示例

### 示例 1：学习一个文件

**输入：**
```
请使用 continuous-knowledge-base 技能学习文件：./docs/project-overview.md
```

**输出：**
```
✅ 文件学习完成
文件名：project-overview.md
提取知识单元：15 个
新增知识：12 个（3 个与现有知识重复）
知识标签：项目概述, 技术栈, 团队介绍, 开发计划

详细统计：
- 总知识单元数：156
- 来源分布：
  * 文件：120
  * 对话：30
  * 手动：6
```

### 示例 2：查询知识

**输入：**
```
请使用 continuous-knowledge-base 技能查询：项目技术栈
```

**输出：**
```
📚 查询结果（显示 5 条，共找到 8 条）：

1. [标签: 技术栈, 项目概述]
   项目采用 React + TypeScript 作为前端框架，后端使用 Node.js + Express，
   数据库使用 PostgreSQL。所有代码使用 Git 进行版本控制。
   来源: ./docs/technical-stack.md
   可信度: 0.95
   ID: kb_001

2. [标签: 技术栈, 开发工具]
   开发团队使用 VS Code 作为主要编辑器，配合 ESLint 和 Prettier 进行代码检查。
   发布流程使用 GitHub Actions 实现 CI/CD。
   来源: conversation_20260515_001
   可信度: 0.88
   ID: kb_042
```

### 示例 3：从对话中学习

**输入：**
```
请使用 continuous-knowledge-base 技能记录以下知识：
项目将在下周五进行第一次用户测试，测试对象为 50 名内部员工。
需要准备测试说明文档和反馈收集表单。
```

**输出：**
```
✅ 知识记录成功
知识单元ID：kb_20260515_133045_abc123
摘要：项目用户测试安排（50名内部员工）
标签：项目计划, 用户测试, 时间安排
可信度：0.90
来源：手动记录
```

### 示例 4：查看统计

**输入：**
```
请使用 continuous-knowledge-base 技能查看统计信息
```

**输出：**
```
📊 知识库统计信息

总知识单元：156
知识来源：
- 文件：120 (76.9%)
- 对话：30 (19.2%)
- 手动：6 (3.8%)

最常出现的标签：
1. 技术栈 (15 个单元)
2. 项目概述 (12 个单元)
3. 开发计划 (10 个单元)

知识更新：
- 创建时间：2026-05-10 10:30:00
- 最后更新：2026-05-15 13:20:00
- 本周新增：23 个单元

最近添加的 5 个单元：
1. kb_... (用户测试安排)
2. kb_... (API 文档更新)
3. kb_... (团队架构调整)
...
```

## 故障排除

- **文件无法读取**：检查文件权限和路径是否正确，确保文件格式受支持
- **知识重复问题**：调整 `similarity_threshold` 参数（配置文件中的 `knowledge_base.similarity_threshold`）
- **查询结果不相关**：考虑启用向量搜索（`vector_enabled: true`），或优化查询关键词
- **性能问题**：对于大型知识库，建议启用向量搜索并使用合适的 embedding 模型
- **存储空间不足**：定期导出并清理过期知识

## 扩展功能

### 1. 启用向量搜索

编辑配置文件，设置 `"vector_enabled": true`，知识库将使用语义向量搜索，提供更准确的查询结果。

首次启用时会自动下载 embedding 模型（约 100MB），需要网络连接。

### 2. 自定义标签系统

知识库会自动提取关键词作为标签，你也可以在添加知识时手动指定标签：

```
请使用 continuous-knowledge-base 技能记录知识：
[内容]
，标签为：[标签1, 标签2, 标签3]
```

### 3. 批量操作

支持批量文件学习、批量导出等功能。具体格式参考配置文件示例。

## 版本更新

### v1.0.0 (当前版本)
- 初始版本
- 支持多种文件格式学习（txt、md、json、pdf、docx）
- 对话学习功能
- 基于关键词和相似度的检索
- 去重和更新机制
- 知识库统计和导出功能
- 可配置的参数系统
