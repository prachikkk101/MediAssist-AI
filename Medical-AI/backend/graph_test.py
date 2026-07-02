from app.graph.workflow import workflow


state = {

    "report_text": """
    Hemoglobin : 10.8
    WBC : 9200
    Platelets : 210000
    """,

    "previous_report": """
    Hemoglobin : 9.5
    WBC : 8500
    Platelets : 200000
    """,

    "parsed_report": {},

    "question": "Compare my previous report",

    "context": "",

    "answer": "",

    "summary": "",

    "nutrition": "",

    "history": "",

    "route": ""

}


result = workflow.invoke(state)



print("\n===================")
print("ANSWER")
print("===================")

print(result.get("answer"))



print("\n===================")
print("SUMMARY")
print("===================")

print(result.get("summary"))



print("\n===================")
print("NUTRITION")
print("===================")

print(result.get("nutrition"))



print("\n===================")
print("HISTORY")
print("===================")

print(result.get("history"))