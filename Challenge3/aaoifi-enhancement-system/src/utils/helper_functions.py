def load_json(file_path):
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    import json
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def validate_data(data, schema):
    from jsonschema import validate, ValidationError
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return False, e.message
    return True, "Data is valid"

def format_report(report_data):
    formatted_report = ""
    for key, value in report_data.items():
        formatted_report += f"{key}: {value}\n"
    return formatted_report.strip()