from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.agent.nodes.answer import answer_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.retrieval import retrieval_node
from app.agent.nodes.router import router_node


def route_after_router(
    state: AgentState,
) -> str:
    """
    简单任务跳过 Planner。
    复杂任务进入 Planner。
    """

    if state["complexity"] == "complex":
        return "planner"

    return "retrieval"


def build_graph():

    builder = StateGraph(
        AgentState
    )

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

    builder.add_edge(
        START,
        "router",
    )

    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "planner": "planner",
            "retrieval": "retrieval",
        },
    )

    builder.add_edge(
        "planner",
        "retrieval",
    )

    builder.add_edge(
        "retrieval",
        "answer",
    )

    builder.add_edge(
        "answer",
        END,
    )

    graph = builder.compile()

    return graph


research_graph = build_graph()