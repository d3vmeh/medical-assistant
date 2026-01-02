from llm_recording import create_record
from json_tools import get_notes_text, get_notes_from_jsonl, load_jsonl_to_dict


condition_map = {
    "chf": "congestive heart failure",
    "hf": "heart failure",
    "sob": "shortness of breath",
    "htn": "hypertension",
    "t2dm": "type 2 diabetes mellitus",
    "pneumonia": "pneumonia",
    }


med_map = {
    "lasix": "furosemide",
    "glucophage": "metformin"
}


def normalize_str(s: str):
    return s.lower().strip()
    
def standardize_list(items, mapping):
    out = set()
    for item in items:
        key = normalize_str(item)
        # Treating "none" as empty for allergies
        if key in {"none", "no known", "nka", "nkda"}:
            continue
        out.add(mapping.get(key, key))
    return out

def predicted_sets(assistant_record):
    extraction = assistant_record["extraction"]

    predicted_conditions = set()
    for condition in extraction.get("conditions", []):
        # Skips anything listed as negated, e.g. ignores "denies chest pain"
        if condition.get("negated", False):
            continue
        
        name = normalize_str(condition["name"])

        # Standardizing abbreviations 
        predicted_conditions.add(condition_map.get(name, name))

    predicted_meds = set()
    for med in extraction.get("medications", []):
        name = normalize_str(med["name"])
        predicted_meds.add(med_map.get(name, name))

    predicted_allergies = {normalize_str(a) for a in extraction.get("allergies", [])}
    
    # Removing any none/unknown instances
    predicted_allergies = {a for a in predicted_allergies if a not in {"none", "no known", "nka", "nkda"}}
    
    return predicted_conditions, predicted_meds, predicted_allergies


def score(prediction: set, original_set: set):
    tp = len(prediction & original_set) # True positive (overlap)
    fp = len(prediction - original_set) # False positive (hallucinations)
    fn = len(original_set - prediction) # False negative (LLM missed these)
    if tp + fp == 0:
        precision = 1.0
    else:
        precision = tp / (tp + fp)
    
    if (tp + fn) == 0:
        recall = 1.0
    else:
        recall = tp / (tp + fn)

    return tp, fp, fn, precision, recall



assistant_path = "eval_data/assistant_eval.jsonl"
eval_path = "eval_data/assistant_eval.jsonl"
open(eval_path, "w").close()


assistant = load_jsonl_to_dict(assistant_path, "source_id")
eval_data = load_jsonl_to_dict(eval_path, "source_id")

totals = {
    "condition": {"tp":0,"fp":0,"fn":0},
    "med": {"tp":0,"fp":0,"fn":0},
    "all": {"tp":0,"fp":0,"fn":0},
}


i = 1
for note_text in get_notes_text():
    source_id = f"note_{i}"
    create_record(note_text, source_id, eval_path)
    print(f"Created record for {source_id}")

    i += 1


