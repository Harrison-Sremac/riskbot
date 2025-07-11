def parse_alert(data):
    return {
        "title": data.get("alert_type", "Unknown Alert"),
        "details": data.get("description", "No details provided.")
    }