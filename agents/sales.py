from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.prompts import SALES_AGENT_PROMPT
from config.setting import llm
from tools.inventory import sales_tools


prompt = ChatPromptTemplate.from_messages(
    [
        ("system",SALES_AGENT_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), # 留给模型思考工具调用的空间
    ]
)

sales_agent = create_tool_calling_agent(llm, tools=sales_tools,prompt=prompt)

sales_agent_executor  = AgentExecutor(
    agent=sales_agent,
    tools=sales_tools,
    verbose=True, # 开启调试模式，可以在控制台看到模型调用工具的过程
    handle_parsing_errors=True
)