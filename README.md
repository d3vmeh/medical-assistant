# Clinical Note Structuring with LLMs

LLM-powered system for converting **unstructured clinical notes** into **structured data** using strict schemas, evidence tracking, and safety constraints.  
The focus is on **information extraction**, not diagnosis or clinical decision-making.

---

## Features

### Structured Clinical Extraction
- Convert free-text clinical notes into validated JSON
- Enforce a strict schema using Pydantic
- Prevent hallucinations through schema-constrained outputs

### Evidence-Preserved Outputs
- Every extracted condition or medication includes a **verbatim evidence quote**
- Enables auditability and traceability back to the source text

### Handles Negation & Uncertainty
  - **Negation** (e.g., “denies chest pain”)
  - **Uncertainty** (e.g., “possible”, “rule out”, “vs”, “?”)

### Safe by Design
- No diagnoses
- No inference of missing facts
- No treatment recommendations

### Storage
- Outputs saved in `.jsonl` format

---

## Project Structure

