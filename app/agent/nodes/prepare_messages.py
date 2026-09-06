from langchain_core.messages import HumanMessage

from app.agent.state import AgentState


def prepare_messages_node(
    state: AgentState,
) -> AgentState:
    """
    将用户 query 转换为 LangGraph Tool Agent 使用的消息格式。
    """

    return {
        "messages": [
            HumanMessage(
                content=state["query"]
            )
        ]
    }