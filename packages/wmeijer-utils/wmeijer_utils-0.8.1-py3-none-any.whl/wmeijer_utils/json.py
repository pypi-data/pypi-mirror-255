import json


def load_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as json_doc:
        j_data = json.loads(json_doc.read())
    return j_data
