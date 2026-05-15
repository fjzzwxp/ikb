**可迭代知识库 (Iterative Knowledge Base)** 是一个为 OpenClaw 智能体打造的技能插件。它从根本上解决了 AI “每次对话都从头开始” 的痛点——你可以将任意文档（PDF、Word、Markdown）喂给它，它会把内容切分、向量化后存入本地知识库；更重要的是，在你们日常对话中，它能自动识别并沉淀有价值的新信息（比如你的偏好、项目约定、重要结论）。下次你再问相关问题时，它便能从不断成长的“第二大脑”中召回最相关的内容，给出越来越精准的回答。整个知识库运行在你自己的设备上，无需担心数据外泄。
# 📚 Iterative Knowledge Base (IKB)

[![OpenClaw Plugin](https://img.shields.io/badge/OpenClaw-Plugin-6366f1)](https://github.com/openclaw)
[![Version](https://img.shields.io/github/v/release/fjzzwxp/ikb)](https://github.com/fjzzwxp/ikb/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **让 OpenClaw 拥有持续学习、不断迭代的“第二大脑”**  
> 支持文档导入 + 对话知识自动沉淀，通过语义级检索让 AI 越用越懂你。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 📄 多格式文档注入 | 支持 PDF、Word (.docx)、Markdown、纯文本，自动提取文本并智能分块 |
| 🧠 对话知识自动捕捉 | 自动识别并提炼对话中有价值的信息（偏好、约定、结论），存入知识库 |
| 🔍 语义检索 | 基于向量 Embedding 检索最相关的内容，支持相似度阈值过滤 |
| ⚡ 混合检索（可选） | 结合向量语义 + BM25 关键词，提高召回准确度 |
| 💾 本地向量数据库 | 使用 LanceDB / Chroma，数据完全私有，不上传任何云端 |
| 🛠️ 开箱即用 | 提供清晰的 Tools（kb_ingest, kb_retrieve, kb_list, kb_delete, kb_summary） |

## 🎯 适用场景

- **个人知识助手**：把散落的笔记、文档、聊天记录变成可检索的知识库
- **团队内部 FAQ**：上传产品手册、会议纪要，AI 随时回答
- **长期记忆 Agent**：让 OpenClaw 记住你的偏好、项目背景、历史决策
- **持续学习系统**：每次对话都沉淀新经验，知识库越用越丰富

## 📦 安装

### 从 GitHub 直接安装（推荐）

```bash
# 安装最新版本
openclaw plugins install git:github.com/fjzzwxp/ikb.git

# 安装指定版本（更稳定）
openclaw plugins install git:github.com/fjzzwxp/ikb.git@v1.0.0
