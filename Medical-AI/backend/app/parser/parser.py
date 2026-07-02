import re


def parse_medical_report(text: str):
    """
    Parse common laboratory values from a medical report.
    Returns a dictionary of extracted values.
    """

    data = {}

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # -------------------------
        # Blood Pressure
        # Example:
        # Blood Pressure: 168/102 mmHg
        # -------------------------
        bp = re.search(
            r"Blood Pressure\s*:\s*(\d+)\s*/\s*(\d+)",
            line,
            re.IGNORECASE,
        )

        if bp:
            data["blood_pressure_systolic"] = int(bp.group(1))
            data["blood_pressure_diastolic"] = int(bp.group(2))
            continue

        # -------------------------
        # Generic numeric values
        # Example:
        # HbA1c: 8.2%
        # Weight: 84 kg
        # Pulse: 82 bpm
        # Fasting Blood Glucose: 176 mg/dL
        # -------------------------
        match = re.search(
            r"^([A-Za-z0-9\s()/\-]+?)\s*:\s*([0-9]+(?:\.[0-9]+)?)",
            line,
            re.IGNORECASE,
        )

        if not match:
            continue

        key = (
            match.group(1)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        value = match.group(2)

        try:

            if "." in value:
                value = float(value)
            else:
                value = int(value)

            data[key] = value

        except ValueError:
            pass

    return data