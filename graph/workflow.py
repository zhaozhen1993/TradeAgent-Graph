from typing import Literal

from langgraph.graph import StateGraph, START, END

from config.logger import get_logger
from config.setting import llm
from agents.prompts import SUPERVISOR_PROMPT
from agents.sales import sales_agent_executor
from agents.logistics import logistics_agent_executor
from agents.support import support_agent_executor

from .state import AgentState

logger = get_logger()


# ── 主管节点：意图识别与路由分发 ──

def supervisor_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content if state["messages"] else ""
    logger.info("主管收到消息: %s", last_msg[:80])

    prompt = f"""
    {SUPERVISOR_PROMPT}
    当前的对话历史如下：
    {state['messages']}
    请只回复专员的名字（小写），不要输出任何解释。
    """
    try:
        response = llm.invoke(prompt)
        next_agent = response.content.strip().lower()
    except Exception as e:
        logger.error("主管路由失败: %s", e)
        return {"next_agent": "general"}

    valid_agents = ["sales", "logistics", "support", "general"]
    if next_agent not in valid_agents:
        logger.warning("未知路由目标 '%s'，降级为 general", next_agent)
        next_agent = "general"

    logger.info("主管路由 → %s", next_agent)
    return {"next_agent": next_agent}


# ── 售前节点 ──

def sales_node(state: AgentState) -> AgentState:
    logger.info("售前专员开始处理...")
    try:
        chat_history = state["messages"][:-1]
        user_input = state["messages"][-1].content
        result = sales_agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        output = result["output"]
        logger.info("售前专员完成，回复长度: %d 字符", len(output))
        return {"messages": [("assistant", output)]}
    except Exception as e:
        logger.error("售前专员异常: %s", e, exc_info=True)
        return {"messages": [("assistant", "售前系统暂时繁忙，已为您转接人工客服。")]}


# ── 物流节点 ──

def logistics_node(state: AgentState) -> AgentState:
    logger.info("物流专员开始处理...")
    try:
        user_input = state["messages"][-1].content
        result = logistics_agent_executor.invoke({"input": user_input})
        output = result["output"]
        logger.info("物流专员完成，回复长度: %d 字符", len(output))
        return {"messages": [("assistant", output)]}
    except Exception as e:
        logger.error("物流专员异常: %s", e, exc_info=True)
        return {"messages": [("assistant", "物流系统暂时繁忙，已为您转接人工客服。")]}


# ── 售后节点 ──

def support_node(state: AgentState) -> AgentState:
    logger.info("售后专员开始处理...")
    try:
        user_input = state["messages"][-1].content
        result = support_agent_executor.invoke({"input": user_input})
        output = result["output"]
        logger.info("售后专员完成，回复长度: %d 字符", len(output))
        return {"messages": [("assistant", output)]}
    except Exception as e:
        logger.error("售后专员异常: %s", e, exc_info=True)
        return {"messages": [("assistant", "售后系统暂时繁忙，已为您转接人工客服。")]}


# ── 通用闲聊节点 ──

def general_node(state: AgentState) -> AgentState:
    logger.info("通用助手处理闲聊...")
    try:
        response = llm.invoke(state["messages"])
        output = response.content
        logger.info("通用助手完成，回复长度: %d 字符", len(output))
        return {"messages": [("assistant", output)]}
    except Exception as e:
        logger.error("通用助手异常: %s", e, exc_info=True)
        return {"messages": [("assistant", "系统暂时繁忙，请稍后再试。")]}


# ── 路由函数 ──

def route_message(state: AgentState) -> Literal["sales", "logistics", "support", "general"]:
    target = state["next_agent"]
    logger.info("路由决策 → %s", target)
    return target


# ── 工厂函数：构建并编译工作流图 ──

def build_agent_app(checkpointer=None):
    """构建并编译 Agent 工作流图。

    :param checkpointer: BaseCheckpointSaver 实例。
                         传入 None 则使用 MemorySaver（内存模式，重启丢失）。
                         传入 AsyncRedisSaver 则持久化到 Redis。
    :return: 编译后的 LangGraph StateGraph 应用
    """
    from langgraph.checkpoint.memory import MemorySaver

    if checkpointer is None:
        checkpointer = MemorySaver()
        logger.info("会话存储: MemorySaver（内存模式，重启后对话历史丢失）")
    else:
        logger.info("会话存储: %s", type(checkpointer).__name__)

    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("sales", sales_node)
    builder.add_node("logistics", logistics_node)
    builder.add_node("support", support_node)
    builder.add_node("general", general_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_message)

    for agent in ("sales", "logistics", "support", "general"):
        builder.add_edge(agent, END)

    compiled = builder.compile(checkpointer=checkpointer)
    logger.info("Agent 工作流图编译完成，节点: supervisor/sales/logistics/support/general")
    return compiled
