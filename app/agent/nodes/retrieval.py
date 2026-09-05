from app.agent.state import AgentState
from app.rag.retriever import retrieve_documents


def retrieval_node(
    state: AgentState,
) -> AgentState:

    query = state["query"]

    print(
        f"[Retrieval] query={query}"
    )

    documents = retrieve_documents(
        query=query,
        k=8,
    )

    print(
        f"[Retrieval] found {len(documents)} chunks"
    )

    for index, doc in enumerate(
        documents[:3],
        start=1,
    ):
        print(
            f"  {index}. "
            f"{doc.metadata.get('source')} "
            f"page={doc.metadata.get('page')}"
        )

    return {
        "documents": documents,
    }