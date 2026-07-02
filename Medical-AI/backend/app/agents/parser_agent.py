from app.parser.llm_parser import parse_medical_report


def parser_agent(state):
    """
    Parses the extracted medical report into structured JSON
    using the LLM parser.
    """

    print("\n========== PARSER AGENT ==========")

    report_text = state.get("report_text", "").strip()

    if not report_text:
        print("❌ No report text available for parsing.")
        state["parsed_report"] = {}
        state["parser_status"] = "failed"
        return state

    print(f"Report Length: {len(report_text)} characters")

    try:
        parsed_report = parse_medical_report(report_text)

        if isinstance(parsed_report, dict) and parsed_report:

            state["parsed_report"] = parsed_report
            state["parser_status"] = "success"

            print("✅ Parsing completed successfully.")

            print("\n========== PARSED REPORT ==========")
            print(parsed_report)
            print("===================================\n")

        else:

            print("⚠ LLM parser returned empty or invalid data.")

            state["parsed_report"] = {}
            state["parser_status"] = "failed"

    except Exception as e:

        print(f"❌ Parser Agent Error: {e}")

        state["parsed_report"] = {}
        state["parser_status"] = "failed"

    return state