from pydantic import BaseModel, Field
from typing import Optional, List

class MedicationMention(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    evidence: str

class ConditionMention(BaseModel):
    name: str
    icd10_code: Optional[str] = None
    evidence: str
    negated: bool = False
    uncertain: bool = False

class MedicalNoteExtraction(BaseModel):
    source_id: str
    chief_complaint: Optional[str] = None
    conditions: List[ConditionMention] = Field(default_factory=list)
    medications: List[MedicationMention] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    assessment_text: Optional[str] = None
    plan_text: Optional[str] = None
