from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState

from app.agent.nodes.router import (
    router_node,
    route_by_complexity,
)

from app.agent.nodes.planner import (
    planner_node,
)

from app.agent.nodes.retrieval import (
    retrieval_node,
)

from app.agent.nodes.answer import (
    answer_node,
)

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

from app.agent.nodes.force_finalize import (
    force_finalize_node,
)


def build_graph():
    """
    构建 Agent Intelligence Platform 的 LangGraph 工作流。

    Simple Task:
        Router
        → Retrieval
        → Answer
        → END

    Complex Task:
        Router
        → Planner
        → Prepare Messages
        → Agent Executor
        → Tool Loop
        → Finalize
        → END

    Tool Loop 达到最大次数时:
        Agent Executor
        → Force Finalize
        → END
    """

    workflow = StateGraph(
        AgentState
    )

    # ========================
    # Nodes
    # ========================

    workflow.add_node(
        "router",
        router_node,
    )

    workflow.add_node(
        "planner",
        planner_node,
    )

    workflow.add_node(
        "retrieval",
        retrieval_node,
    )

    workflow.add_node(
        "answer",
        answer_node,
    )

    workflow.add_node(
        "prepare_messages",
        prepare_messages_node,
    )

    workflow.add_node(
        "agent_executor",
        agent_executor_node,
    )

    workflow.add_node(
        "tool",
        tool_node,
    )

    workflow.add_node(
        "finalize",
        finalize_node,
    )

    workflow.add_node(
        "force_finalize",
        force_finalize_node,
    )

    # ========================
    # START
    # ========================

    workflow.add_edge(
        START,
        "router",
    )

    # ========================
    # Router
    # ========================

    workflow.add_conditional_edges(
        "router",
        route_by_complexity,
        {
            "simple": "retrieval",
            "complex": "planner",
        },
    )

    # ========================
    # Simple Flow
    # ========================

    workflow.add_edge(
        "retrieval",
        "answer",
    )

    workflow.add_edge(
        "answer",
        END,
    )

    # ========================
    # Complex Flow
    # ========================

    workflow.add_edge(
        "planner",
        "prepare_messages",
    )

    workflow.add_edge(
        "prepare_messages",
        "agent_executor",
    )

    # ========================
    # Agent Tool Routing
    # ========================

    workflow.add_conditional_edges(
        "agent_executor",
        route_after_agent,
        {
            "tools": "tool",
            "finalize": "finalize",
            "force_finalize": "force_finalize",
        },
    )

    # Tool 执行后重新回到 Agent
    workflow.add_edge(
        "tool",
        "agent_executor",
    )

    # 正常结束
    workflow.add_edge(
        "finalize",
        END,
    )

    # 达到 Tool Loop 上限后强制结束
    workflow.add_edge(
        "force_finalize",
        END,
    )

    return workflow.compile()


research_graph = build_graph()
graph = research_graph