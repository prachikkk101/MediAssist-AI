
from app.graph.workflow import workflow

state = {
    "report_text": """
    Hemoglobin: 10.8
    WBC: 9200
    Platelets: 210000
    """,
    "previous_report": """
    Hemoglobin: 9.5
    WBC: 8500
    Platelets: 200000
    """,
    "parsed_report": {},
    "question": "Compare my previous report",
    "context": "",
    "answer": "",
    "summary": "",
    "nutrition": "",
    "history": "",
    "route": "",
    "safe_answer": "",
    "safety_status": "",
}

result = workflow.invoke(
    state,
    config={"configurable": {"thread_id": "medical-test-1"}}
)

print("ROUTE:", result.get("route"))
print("PARSER STATUS:", result.get("parser_status"))
print("SAFETY STATUS:", result.get("safety_status"))
print("\nFINAL REVIEWED OUTPUT:")
print(result.get("safe_answer", ""))
