from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PairingComplete(BaseModel):
    code: str = Field(min_length=6, max_length=12)


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    context: str | None = Field(default=None, max_length=2000)
    source_language: str = Field(default="de", min_length=2, max_length=12)
    target_language: str = Field(default="en", min_length=2, max_length=12)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("selection must not be blank")
        return value


class OccurrenceCreate(BaseModel):
    selected_text: str = Field(min_length=1, max_length=500)
    source_sentence: str | None = Field(default=None, max_length=2000)
    page_title: str | None = Field(default=None, max_length=500)
    page_url: HttpUrl | None = None
    source_domain: str | None = Field(default=None, max_length=255)


class MeaningCreate(BaseModel):
    translation: str | None = Field(default=None, max_length=1000)
    definition: str | None = None
    context_note: str | None = None
    provider: str | None = Field(default=None, max_length=100)
    confidence: str = Field(default="unknown", max_length=30)


class ItemCreate(BaseModel):
    original_text: str = Field(min_length=1, max_length=500)
    lemma_or_canonical_text: str | None = Field(default=None, max_length=500)
    item_type: Literal["word", "phrase", "sentence"]
    source_language: str = "de"
    target_language: str = "en"
    translation: str | None = Field(default=None, max_length=1000)
    article: str | None = Field(default=None, max_length=32)
    plural: str | None = Field(default=None, max_length=500)
    infinitive: str | None = Field(default=None, max_length=500)
    verb_forms: str | None = None
    separable: bool | None = None
    required_preposition: str | None = Field(default=None, max_length=100)
    required_case: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    topic: str | None = Field(default=None, max_length=200)
    occurrence: OccurrenceCreate | None = None
    meaning: MeaningCreate | None = None
    duplicate_action: Literal["reject", "create_new", "attach_occurrence"] = "reject"
    card_types: list[Literal["recognition", "production", "cloze", "article", "source_sentence"]] = Field(
        default_factory=lambda: ["recognition", "production", "cloze", "article"], max_length=5
    )

    @field_validator("original_text")
    @classmethod
    def normalize_original(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("original_text must not be blank")
        return value


class ItemPatch(BaseModel):
    translation: str | None = Field(default=None, max_length=1000)
    item_type: Literal["word", "phrase", "sentence"] | None = None
    article: str | None = Field(default=None, max_length=32)
    plural: str | None = Field(default=None, max_length=500)
    infinitive: str | None = Field(default=None, max_length=500)
    verb_forms: str | None = None
    separable: bool | None = None
    required_preposition: str | None = Field(default=None, max_length=100)
    required_case: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    topic: str | None = Field(default=None, max_length=200)
    status: Literal["new", "learning", "reviewing", "known", "suspended"] | None = None


class ReviewSubmission(BaseModel):
    rating: Literal["again", "hard", "good", "easy"]
    response: str | None = Field(default=None, max_length=4000)
    response_time_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    was_correct: bool | None = None


class ImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1]
    exported_at: datetime
    application_version: str
    data: dict
    duplicate_handling: Literal["skip", "create_new"] = "skip"
