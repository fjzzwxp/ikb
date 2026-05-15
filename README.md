# OpenClaw Continuous Knowledge Base Skill

[![GitHub license](https://img.shields.io/github/license/openclaw/continuous-knowledge-base)](https://github.com/openclaw/continuous-knowledge-base/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

A powerful continuous learning knowledge base skill for OpenClaw agent framework. This skill enables OpenClaw to maintain an ever-growing knowledge base from files and conversations.

## Features

- 📚 **Multi-format File Learning**: Extract knowledge from txt, md, json, csv, pdf, docx files
- 💬 **Conversation Learning**: Automatically extract valuable knowledge from dialogues
- 🔍 **Intelligent Search**: Keyword matching with relevance ranking
- 🔄 **Auto Deduplication**: Prevent duplicate knowledge based on content similarity
- 📊 **Knowledge Management**: Statistics, export, and maintenance tools
- ⚡ **Extensible Architecture**: Easy to add new file formats and features

## Quick Start

### Installation

```bash
git clone https://github.com/openclaw/continuous-knowledge-base.git
cd continuous-knowledge-base
```

### Basic Usage

```bash
# Learn from files
python scripts/main.py "学习文件: ./docs/project-overview.md"

# Record knowledge manually
python scripts/main.py "记录知识: OpenClaw is an agent framework"

# Search knowledge
python scripts/main.py "查询: Agent"

# View statistics
python scripts/main.py "统计"

# Export knowledge base
python scripts/main.py "导出为 json"
```

### For OpenClaw Agent Integration

```python
from continuous_knowledge_base import ContinuousKnowledgeBaseSkill

# Initialize skill
skill = ContinuousKnowledgeBaseSkill()

# Process commands from agent
result = skill.run("学习文件: ./data/knowledge.txt")
print(result)
```

## Project Structure

```
continuous-knowledge-base/
├── SKILL.md                    # Skill documentation for OpenClaw
├── config/
│   └── config.json             # Configuration file
├── scripts/
│   ├── main.py                 # Main entry point
│   ├── knowledge_base.py       # Core knowledge base implementation
│   ├── file_processor.py       # File processing utilities
│   └── conversation_learner.py # Dialogue learning module
├── knowledge/
│   └── knowledge_db.json       # Knowledge storage
└── docs/                       # Documentation files
```

## Supported Commands

| Command | Description | Example |
|---------|-------------|---------|
| `学习文件: <path>` | Learn from files | `学习文件: ./docs/readme.md` |
| `记录知识: <content>` | Record knowledge manually | `记录知识: AI is awesome` |
| `查询: <keyword>` | Search knowledge base | `查询: machine learning` |
| `统计` | View statistics | `统计` |
| `导出为 <format>` | Export knowledge base | `导出为 json` |
| `查看: <id>` | View knowledge unit detail | `查看: kb_abc123` |
| `删除: <id>` | Delete knowledge unit | `删除: kb_abc123` |

## Configuration

Edit `config/config.json` to customize behavior:

```json
{
  "knowledge_base": {
    "storage_path": "./knowledge/knowledge_db.json",
    "similarity_threshold": 0.85,
    "max_file_size_mb": 10
  },
  "learning": {
    "auto_learn_from_conversation": true,
    "confidence_threshold": 0.7
  },
  "search": {
    "default_results": 5,
    "max_results": 20
  }
}
```

## Optional Dependencies

Install additional packages for extended functionality:

```bash
# PDF support
pip install pdfplumber

# DOCX support
pip install python-docx

# Vector search (semantic search)
pip install sentence-transformers
```

## Usage Examples

### Learning from Multiple Files

```bash
python scripts/main.py "学习文件: ./docs/project.md ./docs/api.md"
```

### Recording with Tags

```bash
python scripts/main.py "记录知识: OpenClaw uses Skill system for extensibility. 标签为: OpenClaw, Skill, Architecture"
```

### Search with Result Limit

```bash
python scripts/main.py "查询: AI 并返回 10 条结果"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

- GitHub Issues: [https://github.com/openclaw/continuous-knowledge-base/issues](https://github.com/openclaw/continuous-knowledge-base/issues)
- Documentation: [docs/](docs/)

## Acknowledgments

- Built for OpenClaw Agent Framework
- Inspired by knowledge management systems
