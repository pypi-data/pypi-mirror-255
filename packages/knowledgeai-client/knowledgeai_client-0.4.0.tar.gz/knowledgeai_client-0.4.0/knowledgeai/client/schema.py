from enum import StrEnum
from typing import List

import iso639
from pydantic import BaseModel, Field


class ProjectConfigKey(StrEnum):
    BOTSERVICE_APP_ID = "botservice_app_id"
    BOTSERVICE_APP_PASSWORD = "botservice_app_pwd"  # pragma: allowlist secret
    BOTSERVICE_SECRET = "botservice_secret"  # pragma: allowlist secret
    WELCOME_MESSAGE = "welcome_message"
    # TODO: eventually add the model configuration parameters here, e.g. OPENAI_BASE_MODEL, etc.


class Plan(StrEnum):
    FREE = "Free"
    BASIC = "Basic"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"


class IsoLanguage(StrEnum):
    GERMAN = iso639.Language.from_part1("de").part1  # German
    ENGLISH = iso639.Language.from_part1("en").part1  # English


class LLM(StrEnum):
    OPENAI = "OpenAI"
    GOOGLE = "Google"
    ANTHROPIC = "Anthropic"


class User(BaseModel):
    id: int = Field(default=0)
    api_key: str = Field(default="")
    name: str
    company: str
    language: IsoLanguage = Field(default=IsoLanguage.GERMAN)
    plan: Plan = Field(default=Plan.BASIC)
    llm: LLM = Field(default=LLM.OPENAI)


class ProjectDocument(BaseModel):
    project_id: int
    id: int
    name: str
    hash: str


class Project(BaseModel):
    id: int
    name: str
    language: IsoLanguage = Field(default=IsoLanguage.GERMAN)
    model: LLM = Field(default=LLM.OPENAI)
    prompt: str | None = None

    number_of_documents: int = 0
    storage_size: int = 0

    documents: List[ProjectDocument] = []
    configuration: dict[str, str] = {}


class SourceDocument(BaseModel):
    page: str
    content: str
    source: str
    title: str


class AskResponse(BaseModel):
    question: str
    answer: str
    source_paragraphs: List[str]
    source_documents: List[SourceDocument]


class Retriever(StrEnum):
    default: str = "default"
    multiquery: str = "multiquery"
    compression: str = "compression"


class RetrievedDocument(BaseModel):
    content: str
    metadata: dict[str, str]
