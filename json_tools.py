import os
import json

def get_notes_text():
    notes = []
    for filename in os.listdir("test_data"):
        with open(f"test_data/{filename}",'r') as file:
            notes.append(file.read().strip())
    return notes

def append_jsonl(path: str, record: dict):
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

def get_notes_from_jsonl(path: str):
    notes = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            notes.append(json.loads(line))

    print(notes)
    return notes