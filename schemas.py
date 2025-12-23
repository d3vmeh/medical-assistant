from pydantic import BaseModel
from typing import Optional, List

class MedicationMention(BaseModel):
    name: str
    dose: Optional[str]
    frequency: Optional[str]
    evidence: str

class ConditionMention(BaseModel):
    name: str
    icd10_code: Optional[str]
    evidence: str
    negated: bool = False
    uncertain: bool = False

class MedicalNoteExtraction(BaseModel):
    chief_complaint: Optional[str]
    conditions: List[ConditionMention]
    medications: List[MedicationMention]
    allergies: List[str]
    assessment_text: Optional[str]
    plan_text: Optional[str]