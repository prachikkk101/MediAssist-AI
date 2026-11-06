
from typing import TypedDict, Any


class MedicalState(TypedDict, total=False):
    # Input
    file_path: str
    report_text: str
    previous_report: str
    question: str

    # Parsed report and retrieved knowledge
    parsed_report: dict[str, Any]
    context: str
    parser_status: str

    # Agent outputs
    answer: str
    summary: str
    nutrition: str
    history: str

    # Routing and safety
    route: str
    safe_answer: str
    safety_status: str
    analysis: str
