ecommerce_agent/
├── .env                          # 【环境配置文件】存放敏感信息（如 DASHSCOPE_API_KEY）
├── requirements.txt              # 【依赖清单】列出项目所需的 Python 库（langchain, langgraph 等）
├── main.py                       # 【程序入口】FastAPI 启动文件，提供对外 API 接口
│
├── config/                       # 【配置模块】
│   ├── __init__.py
│   └── settings.py               # 加载环境变量，初始化通义千问（ChatTongyi）大模型实例
│
├── agents/                       # 【智能体核心模块】存放各个智能体的定义和提示词
│   ├── __init__.py
│   ├── prompts.py                # 集中管理所有 Agent 的 System Prompt（售前、物流、售后人设）
│   ├── supervisor.py             # 主管智能体（路由逻辑，负责意图识别与分发）
│   ├── sales.py                  # 售前智能体（处理产品、报价、库存）
│   ├── logistics.py              # 物流智能体（处理运费、发货方式）
│   └── support.py                # 售后智能体（处理退换货、政策咨询）
│
├── tools/                        # 【工具模块】封装对外部业务系统的调用
│   ├── __init__.py
│   ├── inventory_tools.py        # 封装库存查询、实时价格计算等 API 接口
│   └── logistics_tools.py        # 封装运费估算、物流轨迹查询等 API 接口
│
├── rag/                          # 【知识库模块】处理外贸文档的检索增强生成（RAG）
│   ├── __init__.py
│   ├── vector_store.py           # 向量数据库的初始化与连接（如阿里云 DashVector 或本地 FAISS）
│   └── retriever.py              # 封装文档检索逻辑，供各智能体调用
│
├── graph/                        # 【工作流编排模块】使用 LangGraph 组装多智能体
│   ├── __init__.py
│   ├── state.py                  # 定义全局共享状态（AgentState，包含对话历史、下一步执行者等）
│   └── workflow.py               # 构建 LangGraph 图结构，连接主管与各个专员智能体
│
└── data/                         # 【数据目录】存放待导入的知识库源文件（如产品手册.pdf、外贸术语.xlsx）
    ├── product_manual.pdf
    └── trade_terms.xlsx