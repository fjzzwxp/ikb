# 技术栈详细说明

## 核心依赖

| 组件 | 技术选型 | 版本要求 | 用途 |
|------|----------|----------|------|
| 运行时 | Python | 3.9+ | 基础运行环境 |
| Web 框架 | FastAPI | >=0.68.0 | API 服务 |
| 异步支持 | asyncio | 内置 | 并发处理 |
| LLM 接口 | openai | >=0.27.0 | AI 模型调用 |
| HTTP 客户端 | httpx | >=0.23.0 | 外部请求 |
| 数据验证 | pydantic | >=1.9.0 | 配置验证 |

## 可选依赖

### 知识库功能
```bash
pip install sentence-transformers  # 向量搜索
pip install pdfplumber            # PDF 支持
pip install python-docx           # DOCX 支持
```

### 开发工具
```bash
pip install black      # 代码格式化
pip install flake8     # 代码检查
pip install pytest     # 测试框架
```

## 部署方式

### 方式 1: 本地部署（推荐开发）

```bash
# 克隆项目
git clone https://github.com/openclaw/core.git

# 安装依赖
pip install -r requirements.txt

# 运行
python -m openclaw.agent --config config.yaml
```

### 方式 2: Docker

```bash
docker build -t openclaw:latest .
docker run -p 8000:8000 openclaw:latest
```

Dockerfile 示例：
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "openclaw.agent", "--config", "config.yaml"]
```

### 方式 3: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw-agent
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: openclaw
        image: openclaw:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENCLAW_CONFIG
          value: "/app/config.yaml"
```

## 配置示例

### config.yaml

```yaml
agent:
  name: "MyClaw"
  llm:
    provider: "openai"
    model: "gpt-4"
    api_key: "${OPENAI_API_KEY}"

skills:
  enabled:
    - web_search
    - code_executor
    - continuous_knowledge_base

knowledge_base:
  storage_path: "./data/knowledge.json"
  vector_enabled: true
  similarity_threshold: 0.85
```

## 性能指标

- **启动时间**: < 2 秒
- **API 响应**: < 100ms（不含 LLM 调用）
- **并发处理**: 100+ 请求同时处理
- **内存占用**: ~150MB（基础运行时 + 一个 LLM Skill）

## 安全考虑

- ✅ API 密钥环境变量存储
- ✅ 请求限流和配额管理
- ✅ 输入验证和清洗
- ✅ CORS 配置
- 🔜 数据加密存储（规划中）
- 🔜 RBAC 权限系统（规划中）

## 扩展性

自定义 Skill 示例：

```python
from openclaw.skill import Skill

class MyCustomSkill(Skill):
    name = "my_skill"
    description = "我的自定义技能"

    async def execute(self, params: dict) -> any:
        # 实现你的逻辑
        return {"result": "success"}
```

## 最佳实践

1. **配置管理**: 使用环境变量替代硬编码
2. **日志记录**: 使用结构化日志
3. **错误处理**: 捕获所有异常，提供友好提示
4. **资源清理**: 使用异步上下文管理器
5. **性能优化**: 利用缓存，减少重复计算

## 常见问题

**Q: 如何添加新的文件格式支持？**

A: 在 `file_processor.py` 的 `SUPPORTED_EXTENSIONS` 中添加扩展名，并实现对应的处理方法。

**Q: 如何调整相似度检测？**

A: 修改 `config.json` 中的 `knowledge_base.similarity_threshold` 参数（0-1）。

**Q: 知识库文件变大了怎么办？**

A: 使用导出和归档功能，定期清理过时内容。考虑启用向量搜索以提高查询性能。
