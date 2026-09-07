from app.agent.nodes.evidence_router import (
    route_after_evidence_check,
)

from app.agent.nodes.query_rewriter import (
    query_rewriter_node,
)

from app.agent.nodes.prepare_retry import (
    prepare_retry_node,
)


from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agent.state import AgentState


# ============================================================
# Router
# ============================================================

from app.agent.nodes.router import (
    router_node,
    route_by_complexity,
)


# ============================================================
# Planner
# ============================================================

from app.agent.nodes.planner import (
    planner_node,
)


# ============================================================
# Simple RAG Flow
# ============================================================

from app.agent.nodes.retrieval import (
    retrieval_node,
)

from app.agent.nodes.answer import (
    answer_node,
)


# ============================================================
# Complex Agent Flow
# ============================================================

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


# ============================================================
# Evidence Checker
# ============================================================

from app.agent.nodes.evidence_checker import (
    evidence_checker_node,
)


# ============================================================
# Build Graph
# ============================================================


def build_graph():
    """
    构建 Agent Intelligence Platform 主工作流。


    Simple Task:

        START
          ↓
        Router
          ↓
        Retrieval
          ↓
        Answer
          ↓
         END


    Complex Task:

        START
          ↓
        Router
          ↓
        Planner
          ↓
        Prepare Messages
          ↓
        Agent Executor
          ↓
        Tool Router
          ↓
        Tool
          ↓
        Agent Executor
          ↓
        ...
          ↓
        Finalize
          ↓
        Evidence Checker
          ↓
         END


    Tool Loop 超限：

        Agent Executor
          ↓
        Force Finalize
          ↓
        Evidence Checker
          ↓
         END
    """

    workflow = StateGraph(
        AgentState
    )

    # ========================================================
    # Register Nodes
    # ========================================================

    workflow.add_node(
        "router",
        router_node,
    )

    workflow.add_node(
        "query_rewriter",
        query_rewriter_node,
    )

    workflow.add_node(
        "prepare_retry",
        prepare_retry_node,
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

    workflow.add_node(
        "evidence_checker",
        evidence_checker_node,
    )

    # ========================================================
    # START
    # ========================================================

    workflow.add_edge(
        START,
        "router",
    )

    # ========================================================
    # Router
    # ========================================================

    workflow.add_conditional_edges(
        "router",
        route_by_complexity,
        {
            "simple": "retrieval",
            "complex": "planner",
        },
    )

    # ========================================================
    # Simple Task Flow
    # ========================================================

    workflow.add_edge(
        "retrieval",
        "answer",
    )

    workflow.add_edge(
        "answer",
        END,
    )

    # ========================================================
    # Complex Task Flow
    # ========================================================

    workflow.add_edge(
        "planner",
        "prepare_messages",
    )

    workflow.add_edge(
        "prepare_messages",
        "agent_executor",
    )

    # ========================================================
    # Agent Tool Routing
    # ========================================================

    workflow.add_conditional_edges(
        "agent_executor",
        route_after_agent,
        {
            "tools": "tool",
            "finalize": "finalize",
            "force_finalize": "force_finalize",
        },
    )

    # ========================================================
    # Tool Loop
    # ========================================================

    # Tool 执行完成后，
    # ToolMessage 会进入 MessagesState，
    # 然后重新交给 Agent 判断下一步。
    workflow.add_edge(
        "tool",
        "agent_executor",
    )

    # ========================================================
    # Normal Finalization
    # ========================================================

    # Agent 不再调用 Tool 后，
    # finalize_node 把最终 AIMessage
    # 写入 state["answer"]。
    workflow.add_edge(
        "finalize",
        "evidence_checker",
    )

    # ========================================================
    # Force Finalization
    # ========================================================

    # Tool Loop 达到最大次数时，
    # force_finalize 根据已经成功执行的
    # Tool Result 生成有限答案。
    workflow.add_edge(
        "force_finalize",
        "evidence_checker",
    )

    # ========================================================
    # Evidence Checker
    # ========================================================

    # 当前阶段 Evidence Checker
    # 只负责评估并写入：
    #
    # evidence_sufficient
    # evidence_score
    # evidence_gaps
    #
    # 暂时不触发 Retry。
    workflow.add_conditional_edges(
        "evidence_checker",
        route_after_evidence_check,
        {
            "end": END,
            "retry": "query_rewriter",
        },
    )


    workflow.add_edge(
        "query_rewriter",
        "prepare_retry",
    )

    workflow.add_edge(
        "prepare_retry",
        "agent_executor",
    )
    # ========================================================
    # Compile
    # ========================================================

    return workflow.compile()


# ============================================================
# Graph Instance
# ============================================================

# run_agent.py 当前使用这个名字
research_graph = build_graph()

# 同时保留 graph 别名，
# 后续其他脚本如果 import graph 也可以正常使用。
graph = research_graph