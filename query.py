import json
import os

from dotenv import load_dotenv
from schemas import MedicalNoteExtraction
from openai import OpenAI


def get_notes():
    notes = []
    for filename in os.listdir("test_data"):
        with open(f"test_data/{filename}",'r') as file:
            notes.append(file.read().strip())
    return notes

def append_jsonl(path: str, record: dict):
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


# Converting abbreviations to standard terms

def standardize_names(name: str, mappings: dict):
    key = name.lower().strip()
    return mappings.get(key, name)

def standardize_extraction(extraction: MedicalNoteExtraction):
    standardize_conditions = {
    "chf": "congestive heart failure",
    "hf": "heart failure",
    "sob": "shortness of breath",
    "htn": "hypertension"
    }

    standardize_meds = {
        "lasix": "furosemide",
        "glucophage": "metformin"
    }
    
    for condition in extraction.conditions:
        condition.name = standardize_names(condition.name, standardize_conditions)

    for medication in extraction.medications:
        medication.name = standardize_names(medication.name, standardize_meds)
    
    return extraction


# Extracting the note and storing in jsonl file

def extract_note(note_text: str, source_id: str):
    
    json_schema = json.dumps(MedicalNoteExtraction.model_json_schema(), indent=2)

    system_prompt = """
    You are an information extractor responsible for extracting structured data from clinical notes.
    Extract only what is explicitly stated. Do not make diagnoses or inferences.
    Return in the format specifically requested, evidence should be copied verbatim.
    """

    prompt_template = """
    You are an information extractor.
    You will be provided clinical medical notes. 
    You must only extract what is stated in the note. Do not make diagnoses or inferences about missing facts.

    You must return a valid JSON (no markdown or extra text) that matches this schema:
    {json_schema}

    Additionally, follow all the rules below in your response:
    - If a field is unknown, use null or an empty list depending on which is appropriate
    - Every condition must contain evidence. This evidence must be quoted exactly how it is listed in the note
    - For negation, only set negated=true is explicitly negated. For example, "no sore throat"
    - For uncertainty, only set uncertain=true if given limits/exceptions. For example, "possible, rule out, ?"
    - Return JSON only. No markdown. No extra text.


    Clinical note (source_id={source_id}):
    \"\"\"{note_text}\"\"\"
    """

    load_dotenv(override=True)

    client = OpenAI()

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"source_id={source_id}\n\nNOTE:\n{note_text}"},
        ],
        text_format=MedicalNoteExtraction
    )

    return response.output_parsed

def create_record(note_text: str, source_id: str):
    extraction = standardize_extraction(extract_note(note_text, source_id))
    record ={
        "source_id": source_id,
        "raw_note": note_text,
        "extraction": extraction.model_dump()
    }
    append_jsonl("notes.jsonl", record)
    return record
