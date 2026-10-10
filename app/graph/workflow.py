from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.core.config import get_settings
from app.services.llm import generate_answer
from app.services.vector_store import search

class RAGState(TypedDict, total=False):
    tenant_id: str
    question: str
    evidence: list[dict]
    grounded: bool
    answer: str

def retrieve_node(state: RAGState) -> RAGState:
    return {
        "evidence": search(
            tenant_id=state["tenant_id"],
            question=state["question"],
            limit=get_settings().top_k,
        )
    }

def evaluate_node(state: RAGState) -> RAGState:
    evidence = state.get("evidence", [])

    grounded = (
        bool(evidence)
        and max(x["score"] for x in evidence)
        >= get_settings().min_evidence_score
    )

    return {
        "grounded": grounded,
        "evidence": evidence if grounded else [],
    }

def route_after_evaluation(state: RAGState) -> str:
    return "generate" if state.get("grounded") else "insufficient"

async def generate_node(state: RAGState) -> RAGState:
    return {"answer": await generate_answer(state["question"], state["evidence"])}

def insufficient_node(state: RAGState) -> RAGState:
    return {
        "grounded": False,
        "evidence": [],
        "answer": (
            "I could not find enough relevant information in the documents "
            "available to this tenant to answer reliably."
        ),
    }

def build_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("generate", generate_node)
    graph.add_node("insufficient", insufficient_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "evaluate")
    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {"generate": "generate", "insufficient": "insufficient"},
    )
    graph.add_edge("generate", END)
    graph.add_edge("insufficient", END)
    return graph.compile()
