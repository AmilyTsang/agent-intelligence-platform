from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState

from app.agent.nodes.answer import answer_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.retrieval import retrieval_node
from app.agent.nodes.router import router_node

from app.agent.nodes.prepare_messages import (
    prepare_messages_node,
)

from app.agent.nodes.agent_executor import (
    agent_executor_node,
)

from app.agent.nodes.tool_node import (
    tool_node,
)

from app.agent.nodes.tool_router import (
    route_after_agent,
)

from app.agent.nodes.finalize import (
    finalize_node,
)


def route_after_router(
    state: AgentState,
) -> str:
    """
    简单任务走传统 RAG。
    复杂任务进入 Agent Tool Loop。
    """

    if state.get(
        "complexity"
    ) == "complex":

        return "planner"

    return "retrieval"


def build_graph():

    builder = StateGraph(
        AgentState
    )


    # ======================
    # 原有节点
    # ======================

    builder.add_node(
        "router",
        router_node,
    )

    builder.add_node(
        "planner",
        planner_node,
    )

    builder.add_node(
        "retrieval",
        retrieval_node,
    )

    builder.add_node(
        "answer",
        answer_node,
    )


    # ======================
    # 新增 Tool Agent 节点
    # ======================

    builder.add_node(
        "prepare_messages",
        prepare_messages_node,
    )

    builder.add_node(
        "agent_executor",
        agent_executor_node,
    )

    builder.add_node(
        "tool",
        tool_node,
    )

    builder.add_node(
        "finalize",
        finalize_node,
    )


    # ======================
    # Entry
    # ======================

    builder.add_edge(
        START,
        "router",
    )


    # ======================
    # Router 分流
    # ======================

    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "planner": "planner",
            "retrieval": "retrieval",
        },
    )


    # ======================
    # Simple RAG Path
    # ======================

    builder.add_edge(
        "retrieval",
        "answer",
    )

    builder.add_edge(
        "answer",
        END,
    )


    # ======================
    # Complex Agent Path
    # ======================

    builder.add_edge(
        "planner",
        "prepare_messages",
    )


    builder.add_edge(
        "prepare_messages",
        "agent_executor",
    )


    # Agent 判断是否调用 Tool

    builder.add_conditional_edges(
        "agent_executor",
        route_after_agent,
        {
            "tools": "tool",
            "finalize": "finalize",
        },
    )


    # Tool 执行完成后回 Agent

    builder.add_edge(
        "tool",
        "agent_executor",
    )


    # 最终回答

    builder.add_edge(
        "finalize",
        END,
    )


    graph = builder.compile()

    return graph


research_graph = build_graph()