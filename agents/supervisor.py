from langchain_core.prompts import ChatPromptTemplate

from agents.prompts import SUPERVISOR_PROMPT

prompt = ChatPromptTemplate(
    [
        ("system",SUPERVISOR_PROMPT)
    ]
)