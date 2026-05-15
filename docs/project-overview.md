# OpenClaw 项目概述

OpenClaw 是一个开源的智能体框架，旨在帮助开发者快速构建和部署自主 AI 助手。

## 项目使命

我们的使命是创建一个**模块化、可扩展、易用**的智能体平台，让每个人都能享受到 AI 带来的便利。

## 核心特性

- ✅ **模块化设计**：核心轻量，通过 Skill 扩展功能
- ✅ **开放生态**：易于集成第三方服务
- ✅ **灵活配置**：支持本地和云端多种部署方式
- ✅ **高性能**：并发处理能力强。

## 技术栈

- **后端**: Python 3.9+
- **通信**: RESTful API + WebSocket
- **存储**: SQLite / PostgreSQL / Redis
- **AI 模型**: OpenAI GPT、Claude 等（支持自定义模型）
- **配置管理**: JSON/YAML

## 项目结构

```
openclaw/
├── core/              # 核心模块
│   ├── agent.py      # 智能体类
│   ├── skill.py      # Skill 基类
│   └── memory.py     # 记忆管理
├── skills/           # 内置技能
│   ├── web_search.py
│   ├── code_executor.py
│   └── ...
├── config/           # 配置文件
└── docs/             # 文档
```

## 发展路线

- **v1.0**: 基础框架（已完成）
- **v1.1**: 增强 Skill 系统（进行中）
- **v1.2**: Web 管理界面（规划中）
- **v2.0**: 分布式部署（规划中）

## 联系我们

- GitHub: github.com/openclaw
- Discord: discord.gg/openclaw
- Email: support@openclaw.ai
