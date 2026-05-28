import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from config.logger import get_logger
from graph.workflow import build_agent_app

logger = get_logger()


# ── 请求 / 响应模型 ──

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    status: str
    response: str
    next_agent: str


# ── 应用生命周期：启动时编译 Agent 图 ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时根据 REDIS_URL 环境变量决定存储后端，编译 Agent 工作流图。"""
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        try:
            from langgraph.checkpoint.redis import AsyncRedisSaver
            checkpointer = await AsyncRedisSaver.from_conn_string(redis_url).__aenter__()
            app.state.agent_app = build_agent_app(checkpointer=checkpointer)
            app.state.checkpointer = checkpointer
            app.state.storage_backend = "redis"
            logger.info("Redis 会话存储已连接: %s", redis_url)
        except Exception as e:
            logger.error("Redis 连接失败 (%s)，降级为内存存储", e)
            app.state.agent_app = build_agent_app()
            app.state.storage_backend = "memory"
    else:
        app.state.agent_app = build_agent_app()
        app.state.storage_backend = "memory"

    logger.info("服务启动完成，存储后端: %s", app.state.storage_backend)
    yield

    # 关闭时释放 Redis 连接
    if app.state.storage_backend == "redis":
        await app.state.checkpointer.__aexit__(None, None, None)
        logger.info("Redis 连接已关闭")


app = FastAPI(
    title="外贸电商多智能体系统",
    description="基于 LangGraph 的多智能体外贸客服系统 — Supervisor + Sales/Logistics/Support 专员",
    version="1.0.0",
    lifespan=lifespan,
)


# ── 全局异常兜底 ──

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("未捕获异常: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "response": "系统内部错误，请稍后再试。", "next_agent": "error"},
    )


# ── API 端点 ──

@app.post("/chat", response_model=ChatResponse)
async def chat(query: ChatRequest):
    """多智能体对话入口。"""
    config = {"configurable": {"thread_id": query.session_id}}
    inputs = {"messages": [("user", query.message)]}

    final_state = await app.state.agent_app.ainvoke(inputs, config)

    last_message = final_state["messages"][-1]
    return ChatResponse(
        status="success",
        response=last_message.content,
        next_agent=final_state.get("next_agent", "unknown"),
    )


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """查询某次会话的完整对话历史。"""
    config = {"configurable": {"thread_id": session_id}}
    state = await app.state.agent_app.aget_state(config)

    if state.values:
        messages = []
        for m in state.values.get("messages", []):
            if hasattr(m, "content"):
                messages.append({"role": m.type, "content": m.content})
        return {"session_id": session_id, "messages": messages}
    return {"session_id": session_id, "messages": []}


@app.get("/health")
async def health():
    """健康检查。"""
    return {
        "status": "ok",
        "storage": app.state.storage_backend,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
