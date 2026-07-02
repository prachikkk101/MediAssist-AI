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


# ---------------------------------------------------
# Create Graph
# ---------------------------------------------------

graph = StateGraph(MedicalState)


# ---------------------------------------------------
# Nodes
# ---------------------------------------------------

graph.add_node("Supervisor", supervisor_agent)
graph.add_node("Parser", parser_agent)
graph.add_node("Retriever", rag_agent)
graph.add_node("Explain", explanation_agent)
graph.add_node("Summary", summary_agent)
graph.add_node("Nutrition", nutrition_agent)
graph.add_node("History", history_agent)


# ---------------------------------------------------
# Entry
# ---------------------------------------------------

graph.set_entry_point("Supervisor")


# ---------------------------------------------------
# Supervisor Routing
# ---------------------------------------------------

def route(state):
    return state["route"]


graph.add_conditional_edges(
    "Supervisor",
    route,
    {
        "explanation": "Parser",
        "nutrition": "Parser",
        "history": "Parser",
        "summary": "Summary",
    },
)


# ---------------------------------------------------
# Parser always goes to Retriever
# ---------------------------------------------------

graph.add_edge(
    "Parser",
    "Retriever"
)


# ---------------------------------------------------
# Retriever Routing
# ---------------------------------------------------

def retriever_route(state):

    route = state["route"]

    if route == "nutrition":
        return "nutrition"

    elif route == "history":
        return "history"

    return "explanation"


graph.add_conditional_edges(
    "Retriever",
    retriever_route,
    {
        "explanation": "Explain",
        "nutrition": "Nutrition",
        "history": "History",
    },
)


# ---------------------------------------------------
# Explanation Path
# ---------------------------------------------------

graph.add_edge(
    "Explain",
    "Summary"
)

graph.add_edge(
    "Summary",
    END
)


# ---------------------------------------------------
# Nutrition Path
# ---------------------------------------------------

graph.add_edge(
    "Nutrition",
    END
)


# ---------------------------------------------------
# History Path
# ---------------------------------------------------

graph.add_edge(
    "History",
    END
)


# ---------------------------------------------------
# Compile
# ---------------------------------------------------

memory = MemorySaver()

workflow = graph.compile(
    checkpointer=memory
)