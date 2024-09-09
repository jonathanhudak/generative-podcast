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

class PromptItem(BaseModel):
    name: str
    id: str

class ScriptItem(BaseModel):
    name: str
    id: str

class PodcastItem(BaseModel):
    name: str
    id: str

class PromptResponse(BaseModel):
    prompts: List[PromptItem]  # List of PromptItem objects

class ScriptResponse(BaseModel):
    scripts: List[ScriptItem]  # List of ScriptItem objects

class PodcastResponse(BaseModel):
    podcasts: List[PodcastItem]  # List of PodcastItem objects