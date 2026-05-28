# 外贸电商多智能体客服系统

> 🤝 本项目的每一行代码都由 **人类开发者** 与 **AI 编程助手** 深度协作完成——从架构设计到代码落地，从 Bug 排查到生产加固，联手打造。

基于 **LangGraph** 的 Supervisor 多智能体外贸电商客服系统，覆盖售前咨询、物流运费、售后支持三大业务场景，集成 RAG 知识库检索与工具调用能力，通过 FastAPI 提供标准化 RESTful 接口。

---

## 架构总览

```
用户消息
  │
  ▼
┌─────────────┐
│  Supervisor │  意图识别 + 路由分发
│   主管节点   │
└──┬───┬───┬──┘
   │   │   │
   ▼   ▼   ▼
┌───┐┌───┐┌───┐
│Sales││Log││Support│  各司其职
│售前 ││物流││售后   │
└─┬──┘└─┬─┘└─┬───┘
  │     │     │
  ▼     ▼     ▼
┌─────────────────┐
│  Tools + RAG    │  查库存 · 算运费 · 搜知识库
│  工具 + 知识库   │
└─────────────────┘
  │
  ▼
 用户回复
```

### 多智能体分工

| 角色 | 职责 | 工具 |
|------|------|------|
| **Supervisor（主管）** | 意图识别，精准分发到对应专员 | — |
| **Sales（售前）** | 产品参数、材质、阶梯报价、库存查询 | `check_stock` `get_tiered_price` `search_knowledge_base` |
| **Logistics（物流）** | 海运/空运费率估算、物流时效 | `estimate_shipping_cost` |
| **Support（售后）** | 退换货政策、售后流程、订单查询 | `search_knowledge_base` |
| **General（通用）** | 闲聊、打招呼等非业务对话 | — |

---

## 核心特性

- **智能路由**：Supervisor 精准识别用户意图，单点分发，避免多 Agent 混乱响应
- **RAG 增强**：基于 Qdrant 向量数据库 + BM25 混合检索，Agent 基于真实知识库回答，杜绝幻觉
- **工具调用**：Agent 自动决策何时调用业务工具（查库存、算运费），无需人工编排
- **生产级日志**：全链路日志追踪——从消息入站 → 路由决策 → Agent 执行 → 异常降级
- **持久化双模式**：默认内存存储，设 `REDIS_URL` 即可升级为 Redis 持久化，服务重启对话不丢
- **标准化接口**：FastAPI RESTful API，自带 Swagger 文档，即插即用

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **Agent 编排** | LangGraph（StateGraph + Supervisor 模式） |
| **大模型** | 通义千问 (qwen-plus) / 兼容 OpenAI 格式的任意模型 |
| **Embedding** | DashScope text-embedding-v3（1024 维） |
| **向量数据库** | Qdrant（本地模式 + 文件持久化） |
| **RAG 检索** | 向量检索 + BM25 混合检索（EnsembleRetriever） |
| **Web 框架** | FastAPI + Uvicorn |
| **会话存储** | MemorySaver（内存）/ Redis（持久化，可选） |
| **文档加载** | Docling（支持 PDF、DOCX、PPTX、TXT） |
| **日志系统** | Python logging（单例模式，全链路追踪） |

---

## 项目结构

```
D:\agent\
├── main.py                  # FastAPI 入口，lifespan 初始化 Agent 图
├── requirements.txt         # 依赖清单
├── .env                     # 环境变量（API Key、Redis 连接等）
│
├── config/                  # 配置模块
│   ├── setting.py           # LLM 初始化
│   └── logger.py            # 单例日志系统
│
├── agents/                  # 智能体核心
│   ├── prompts.py           # 所有 Agent 的 System Prompt
│   ├── supervisor.py        # 主管（路由）
│   ├── sales.py             # 售前 Agent
│   ├── logistics.py         # 物流 Agent
│   └── support.py           # 售后 Agent
│
├── graph/                   # LangGraph 工作流
│   ├── state.py             # AgentState 状态定义
│   └── workflow.py          # 图构建 + 节点函数 + build_agent_app()
│
├── tools/                   # 业务工具
│   ├── inventory.py         # 库存查询、阶梯报价
│   ├── logistics.py         # 国际运费估算
│   └── knowledge.py         # RAG 知识库检索工具
│
├── rag/                     # 知识库模块
│   ├── vector_store.py      # Qdrant 向量库初始化
│   ├── retriever.py         # 混合检索器（向量 + BM25）
│   └── ingest.py            # 知识库数据导入脚本
│
├── services/                # 外部 API 客户端（待对接）
│   ├── base_client.py       # 统一 HTTP 客户端基类
│   ├── erp_client.py        # ERP 系统接口
│   └── wms_client.py        # WMS 物流系统接口
│
└── data/                    # 知识库源文件
    ├── 尺码推荐.txt
    └── 洗涤养护.txt
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd agent
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env`：

```bash
ALIAPI=your_api_key_here
BASEURL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL=qwen-plus
DASHSCOPE_API_KEY=your_dashscope_key
```

### 4. 导入知识库

```bash
python rag/ingest.py
```

输出示例：
```
🚀 开始导入外贸知识库（Qdrant 本地模式）...
📄 成功加载 11 个原始文档
✂️  文档切分为 11 个知识片段
✅ 知识库导入完成！数据保存在 ./data/qdrant_db
```

### 5. 启动服务

```bash
python main.py
```

服务启动日志：
```
2026-05-28 13:00:00 [INFO] ecommerce_agent: 会话存储: MemorySaver（内存模式）
2026-05-28 13:00:00 [INFO] ecommerce_agent: Agent 工作流图编译完成
2026-05-28 13:00:00 [INFO] ecommerce_agent: 服务启动完成，存储后端: memory
```

### 6. 测试

浏览器打开 `http://localhost:8000/docs` 使用 Swagger 在线测试，或：

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "SKU001 100件多少钱？发到美国运费多少？", "session_id": "test-001"}'
```

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/chat` | 多智能体对话入口 |
| `GET` | `/history/{session_id}` | 查询某次会话的完整对话历史 |
| `GET` | `/health` | 健康检查 + 当前存储后端 |

### 请求示例

```json
POST /chat
{
  "message": "SKU001 100件报价多少？发美国运费？",
  "session_id": "user-abc-123"
}
```

### 响应示例

```json
{
  "status": "success",
  "response": "产品 男士纯棉T恤 (SKU001) 采购 100 件，适用阶梯：100-499 (享受95折)。单价：5.22 USD...",
  "next_agent": "sales"
}
```

---

## 升级到 Redis 持久化

```bash
# 1. 启动 Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 2. 在 .env 中设置
REDIS_URL=redis://localhost:6379/0

# 3. 重启服务
python main.py
```

日志会显示：`Redis 会话存储已连接: redis://localhost:6379/0`

---

## 日志示例

一次完整请求的日志链路：

```
2026-05-28 13:00:01 [INFO] ecommerce_agent: 主管收到消息: SKU001 100件多少钱？
2026-05-28 13:00:02 [INFO] ecommerce_agent: 主管路由 → sales
2026-05-28 13:00:02 [INFO] ecommerce_agent: 路由决策 → sales
2026-05-28 13:00:02 [INFO] ecommerce_agent: 售前专员开始处理...
2026-05-28 13:00:05 [INFO] ecommerce_agent: 售前专员完成，回复长度: 156 字符
```

---

## 后续路线图

- [ ] **Phase 2**：Redis 会话持久化（已完成架构适配，设 `REDIS_URL` 即可启用）
- [ ] **Phase 3**：对接真实 ERP / WMS / 物流系统 API
- [ ] **Phase 4**：Docker Compose 一键部署 + 生产加固
- [ ] 对话分析看板（意图分布、热门问题、满意度统计）
- [ ] 多语言前端接入（Web Chat Widget）

---

## 技术亮点

1. **Supervisor 单点分发**：不是把所有 Agent 的输出都丢给用户，而是由主管精准选出最合适的那个，杜绝多 Agent 抢答
2. **RAG 与 Tool 的分离**：知识库检索是 Agent 手里的一个工具，Agent 自己决定什么时候查知识库、查什么——而不是在 workflow 里硬编码
3. **两阶段存储架构**：lifespan 阶段初始化 checkpointer，请求阶段零感知，内存和 Redis 无缝切换
4. **全链路异常兜底**：每个节点独立 try/except + 全局 FastAPI exception handler，单点故障不影响其他路径

---

## 联手之作

本项目由 **人类开发者** 与 **AI 编程助手** 深度协作完成：

| 协作环节 | 人类 | AI |
|----------|------|-----|
| 架构设计 | 确定 Supervisor 多智能体模式、业务分工 | 提供 LangGraph 最佳实践、给出完整路线图 |
| Agent 实现 | 定义业务 Prompt、设计工具接口 | 实现 Tool Calling Agent、编写节点函数 |
| RAG 集成 | 收集知识库文档、确定检索策略 | 搭建 Qdrant 向量库、实现混合检索器 |
| 生产加固 | 提出日志/异常/持久化需求 | 实现全链路日志、异步 lifespan、双模式存储 |
| Bug 排查 | 发现问题、确认根因 | 定位代码、提供修复方案 |
| 文档编写 | 审核内容、确认准确性 | 生成结构化 README 和 API 文档 |

这不是「AI 替你写代码」，而是「你和 AI 一起建系统」——你定方向、做决策，AI 负责执行、查漏、加速。

---

## License

MIT
