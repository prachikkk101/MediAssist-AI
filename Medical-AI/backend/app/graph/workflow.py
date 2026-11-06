from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import MedicalState
from app.agents.supervisor_agent import supervisor_agent
from app.agents.parser_agent import parser_agent
from app.agents.rag_agent import rag_agent
from app.agents.explanation_agent import explanation_agent
from app.agents.summary_agent import summary_agent
from app.agents.nutrition_agent import nutrition_agent
from app.agents.history_agent import history_agent
from app.agents.safety_agent import safety_agent


graph = StateGraph(MedicalState)

graph.add_node("Supervisor", supervisor_agent)
graph.add_node("Parser", parser_agent)
graph.add_node("Retriever", rag_agent)
graph.add_node("Explain", explanation_agent)
graph.add_node("Summary", summary_agent)
graph.add_node("Nutrition", nutrition_agent)
graph.add_node("History", history_agent)
graph.add_node("Safety", safety_agent)

graph.set_entry_point("Supervisor")

KNOWN_ROUTES = {"explanation", "summary", "nutrition", "history", "full_analysis"}


def supervisor_route(state):
    route = state.get("route")
    return route if route in KNOWN_ROUTES else "explanation"


graph.add_conditional_edges(
    "Supervisor",
    supervisor_route,
    {
        "explanation": "Parser",
        "summary": "Parser",
        "nutrition": "Parser",
        "history": "Parser",
        "full_analysis": "Parser",   # used by /medical/upload
    },
)

graph.add_edge("Parser", "Retriever")


def retriever_route(state):
    route = state.get("route")
    if route == "nutrition":
        return "nutrition"
    if route == "history":
        return "history"
    return "explanation"   # explanation, summary, full_analysis


graph.add_conditional_edges(
    "Retriever",
    retriever_route,
    {
        "explanation": "Explain",
        "nutrition": "Nutrition",
        "history": "History",
    },
)

graph.add_edge("Explain", "Summary")


def after_summary(state):
    # Full report analysis also produces the nutrition tab.
    return "nutrition" if state.get("route") == "full_analysis" else "safety"


graph.add_conditional_edges(
    "Summary",
    after_summary,
    {"nutrition": "Nutrition", "safety": "Safety"},
)

graph.add_edge("Nutrition", "Safety")
graph.add_edge("History", "Safety")
graph.add_edge("Safety", END)

memory = MemorySaver()
workflow = graph.compile(checkpointer=memory)