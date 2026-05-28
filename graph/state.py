from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    # add_messages 会自动处理消息列表的追加，避免覆盖历史对话
    messages: Annotated[list, add_messages]
    next_agent: str # 主管决定的下一个执行者


RouteOptions = Literal["sales", "logistics", "support", "general", "FINISH"]