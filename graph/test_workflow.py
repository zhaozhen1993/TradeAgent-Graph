# test_workflow.py
import asyncio
from graph.workflow import app


async def test_agent():
    # 模拟用户输入
    inputs = {"messages": [("user", "你好，我想查一下 SKU001 的库存，同时我是179的身高有什么推荐尺码？")]}

    print("用户提问：", inputs["messages"][0][1])
    print("-" * 30)

    # 异步调用 LangGraph 工作流
    async for event in app.astream(inputs, stream_mode="values"):
        # 打印出每一步的状态变化，方便调试
        if "next_agent" in event:
            print(f"🤖 主管决定交给 -> {event['next_agent']} 处理")
        elif "messages" in event:
            last_msg = event["messages"][-1]
            print(f"💬 回复内容: {last_msg.content}")
            print("-" * 30)


if __name__ == "__main__":
    asyncio.run(test_agent())