import json
from libcoveoc4ids.api import oc4ids_json_output
import os

example_data_path = os.path.join(os.path.dirname(__file__), "example.json")
def extract_messages(errors):
    messages = []
    for error_json_str, locations in errors:
        error = json.loads(error_json_str)
        messages.append(error.get("message"))
    return messages


with open(example_data_path, "r", encoding="utf-8") as f:
    example_data = json.load(f)
    validation_result = oc4ids_json_output(json_data=example_data)
    validation_error = validation_result["validation_errors"]
    print("Validation Errors:", extract_messages(validation_error))