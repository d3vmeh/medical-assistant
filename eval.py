from llm_recording import create_record
from json_tools import get_notes_text, get_notes_from_jsonl, load_jsonl_to_dict
from typing import Tuple, Set

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


assistant_path = "eval_data/assistant_eval.jsonl"
eval_path = "eval_data/eval.jsonl"



def normalize_str(s: str):
    return s.lower().strip()
    
def standardize_set(items, mapping):
    out = set()
    for item in items:
        key = normalize_str(item)
        # Treating "none" as empty for allergies
        if key in {"none", "no known", "nka", "nkda"}:
            continue
        out.add(mapping.get(key, key))
    return out

def predicted_sets(assistant_record):
    """
    pred_record is expected to have:
      pred_record["extraction"]["conditions"], ["medications"], ["allergies"]
    """
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

def eval_sets(eval_record: dict) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    eval_record is expected to have:
      eval_record["conditions"] (list[str])
      eval_record["medications"] (list[str])
      eval_record["allergies"] (list[str])
    """
    eval_conditions = standardize_set(
        eval_record.get("conditions", []),
        condition_map
    )

    eval_meds = standardize_set(
        eval_record.get("medications", []),
        med_map
    )

    eval_allergies = standardize_set(
        eval_record.get("allergies", []),
        {}
    )

    return eval_conditions, eval_meds, eval_allergies

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


def add_totals(totals: dict, key: str, tp: int, fp: int, fn: int):
    totals[key]["tp"] += tp
    totals[key]["fp"] += fp
    totals[key]["fn"] += fn


def totals_to_metrics(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = 1.0 if (tp + fp) == 0 else tp / (tp + fp)
    recall = 1.0 if (tp + fn) == 0 else tp / (tp + fn)
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1

# Clearing the file, regenerate
# open(assistant_path, 'w')

i = 1
for note_text in get_notes_text():
    source_id = f"note_{i}"
    create_record(note_text, source_id, assistant_path)
    print(f"Created record for {source_id}")
    i += 1

assistant_predictions = load_jsonl_to_dict(assistant_path, "source_id")
eval_data = load_jsonl_to_dict(eval_path, "source_id")

# Running totals
totals = {
    "conditions": {"tp":0,"fp":0,"fn":0},
    "meds": {"tp":0,"fp":0,"fn":0},
    "allergies": {"tp":0,"fp":0,"fn":0},
}


# In case the prediction wasn't generated for a note
missing_predictions = []
# In case the predicted note doesn't have a label
missing_evaluations = []

# sid - source id, e - eval record
for sid, e in eval_data.items():
    # Skipping comparison if nothing generated
    if sid not in assistant_predictions:
        missing_predictions.append(sid)
        continue

    p = assistant_predictions[sid]

    p_conds, p_meds, p_all = predicted_sets(p)
    e_conds, e_meds, e_all = eval_sets(e)

    tp, fp, fn, prec, rec = score(p_conds, e_conds)
    add_totals(totals, "conditions", tp, fp, fn)

    tp, fp, fn, prec, rec = score(p_meds, e_meds)
    add_totals(totals, "meds", tp, fp, fn)

    tp, fp, fn, prec, rec = score(p_all, e_all)
    add_totals(totals, "allergies", tp, fp, fn)

for sid in assistant_predictions.keys():
    if sid not in eval_data:
        missing_evaluations.append(sid)

print("=== EVALUATION SUMMARY ===")

for k in ["conditions", "meds", "allergies"]:
    tp = totals[k]["tp"]
    fp = totals[k]["fp"]
    fn = totals[k]["fn"]
    precision, recall, f1 = totals_to_metrics(tp, fp, fn)
    print(f"\n[{k.upper()}]")
    print(f"TP={tp}  FP={fp}  FN={fn}")
    print(f"Precision={precision:.3f}  Recall={recall:.3f}  F1={f1:.3f}")

if missing_predictions:
    print(f"\nMissing predictions for {len(missing_predictions)} eval items: {missing_predictions[:10]}{'...' if len(missing_predictions)>10 else ''}")
if missing_evaluations:
    print(f"\nMissing eval labels for {len(missing_evaluations)} predicted items: {missing_evaluations[:10]}{'...' if len(missing_evaluations)>10 else ''}")


