from pydantic import BaseModel
from typing import Optional, Dict, Any, List



# Pydantic models for request bodies
class PromptRequest(BaseModel):
    topic: str

class ScriptRequest(BaseModel):
    prompt: str

class VoiceLabel(BaseModel):
    accent: str
    description: str
    age: str
    gender: str
    use_case: str

class Voice(BaseModel):
    voice_id: str
    name: str
    category: str
    labels: VoiceLabel

class VoiceResponse(BaseModel):
    voices: List[Voice]

class PromptResponse(BaseModel):
    prompts: list

class ScriptResponse(BaseModel):
    scripts: list

class PodcastResponse(BaseModel):
    podcasts: list