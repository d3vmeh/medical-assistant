from llm_recording import create_record
from json_tools import get_notes_text, get_notes_from_jsonl

i = 1

eval_path = "eval_data/assistant_eval.jsonl"

for note_text in get_notes_text():
    source_id = f"eval_{i}"
    i += 1
    create_record(note_text, source_id, eval_path)

notes = get_notes_from_jsonl(eval_path)
print(notes)
