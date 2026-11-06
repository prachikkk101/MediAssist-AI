from app.parser.llm_parser import parse_medical_report


def has_medical_data(report):
    """Return True if at least one meaningful clinical field exists."""
    if not isinstance(report, dict):
        return False

    clinical_sections = [
        "lab_results",
        "laboratory",
        "vitals",
        "diagnosis",
        "medications",
        "recommendations",
    ]

    def has_value(value):
        if isinstance(value, dict):
            return any(has_value(v) for v in value.values())
        if isinstance(value, list):
            return any(has_value(v) for v in value)
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        return True

    return any(
        has_value(report.get(section))
        for section in clinical_sections
    )


def parser_agent(state):
    """Parse extracted report text and validate clinical fields."""
    print("\n========== PARSER AGENT ==========")

    report_text = state.get("report_text", "").strip()

    if not report_text or state.get("ocr_status") == "failed":
        print("[ERROR] OCR failed or no usable text was extracted.")
        state["parsed_report"] = {}
        state["parser_status"] = "failed"
        state["answer"] = (
            "I could not reliably read this report. "
            "Please upload a clearer image or the original PDF."
        )
        return state

    print(f"Report Length: {len(report_text)} characters")

    try:
        parsed_report = parse_medical_report(report_text)

        if not has_medical_data(parsed_report):
            print("[WARN] No meaningful clinical data was extracted.")
            state["parsed_report"] = {}
            state["parser_status"] = "failed"
            state["answer"] = (
                "I could not reliably identify medical results in this file. "
                "Please upload a clearer report. No medical interpretation "
                "can be provided until the results are readable."
            )
            return state

        state["parsed_report"] = parsed_report
        state["parser_status"] = "success"

        print("[OK] Clinical data extracted.")
        print("\n========== PARSED REPORT ==========")
        print(parsed_report)
        print("===================================")

    except Exception as e:
        print(f"[ERROR] Parser Agent Error: {e}")
        state["parsed_report"] = {}
        state["parser_status"] = "failed"
        state["answer"] = (
            "The report could not be parsed reliably. "
            "Please try uploading a clearer file."
        )

    return state