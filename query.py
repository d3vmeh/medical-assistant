import json

prompt_template = """
You are an information extractor.
You will be provided clinical medical notes. 
You must only extract what is stated in the note. Do not make diagnoses or inferences about missing facts.

You must return a valid JSON that matches this schema:
{json_schema}

Additionally, follow all the rules below in your response:
- If a field is unknown, use null or an empty list depending on which is appropriate
- Every condition must contain evidence



Clinical note (source_id={source_id}):
\"\"\"{note_text}\"\"\"
"""