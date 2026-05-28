from langchain_classic.agents import create_tool_calling_agent,AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.prompts import LOGISTICS_AGENT_PROMPT
from config.setting import llm
from tools.logistics import logistics_tools

prompt = ChatPromptTemplate(
    [
        ("system",LOGISTICS_AGENT_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

logistics_agent = create_tool_calling_agent(llm,tools=logistics_tools,prompt=prompt)

logistics_agent_executor = AgentExecutor(
    agent=logistics_agent,
    tools=logistics_tools,
    verbose=True, # 开启调试模式，可以在控制台看到模型调用工具的过程
    handle_parsing_errors=True
)