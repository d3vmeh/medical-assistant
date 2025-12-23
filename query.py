import json
from dotenv import load_dotenv
from schemas import MedicalNoteExtraction
from anthropic import Anthropic
from openai import OpenAI

load_dotenv(override=True)

json_schema = json.dumps(MedicalNoteExtraction.model_json_schema(), indent=2)


client = OpenAI()

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
- Every condition must contain evidence. THis evidence must be quoted exactly how it is listed in the note
- For negation, only set negated=true is explicitly negated. For example, "no sore throat"
- For uncertainty, only set uncertain=true if given limits/exceptions. For example, "possible, rule out, ?"
- Return JSON only. No markdown. No extra text.


Clinical note (source_id={source_id}):
\"\"\"{note_text}\"\"\"
"""


def extract_note(note_text: str, source_id: str):

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"source_id={source_id}\n\nNOTE:\n{note_text}"},
        ],
        text_format=MedicalNoteExtraction
    )

    return response.output_parsed

note = (
        "67M with hx CHF. Worsening dyspnea x2 days. BNP 1200. "
        "On furosemide 40 mg daily. Allergies: penicillin. "
        "Plan: increase diuretics, repeat BMP tomorrow."
)
extraction = extract_note(note, "note-001")
print(extraction.model_dump_json(indent=2))