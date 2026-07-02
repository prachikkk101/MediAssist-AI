from typing import TypedDict

class MedicalState(TypedDict):
    report_text: str

    parsed_report: str

    question: str
    context: str

    answer: str
    summary: str



    nutrition:str
    history: str
    route: str