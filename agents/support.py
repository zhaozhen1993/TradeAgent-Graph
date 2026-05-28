from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.prompts import SUPPORT_AGENT_PROMPT
from config.setting import llm
from tools.knowledge import search_knowledge_base

prompt = ChatPromptTemplate([
    ("system",SUPPORT_AGENT_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user","{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

support_agent = create_tool_calling_agent(
    llm,
    tools=[search_knowledge_base],
    prompt=prompt

)

support_agent_executor = AgentExecutor(
    agent=support_agent,
    tools=[search_knowledge_base]
)