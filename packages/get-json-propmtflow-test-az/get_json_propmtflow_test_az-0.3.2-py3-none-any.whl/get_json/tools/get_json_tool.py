from promptflow import tool
import json


@tool
def get_json_object(input_text: str) -> str:
    # JSON-String in ein Python-Dictionary umwandeln
    person_dict = json.loads(input_text)

    # Den Wert des Schlüssels "Name" abrufen
    name = person_dict["Name"]
    return str(name)