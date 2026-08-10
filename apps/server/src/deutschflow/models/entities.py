from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from deutschflow.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AppSetting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    source_language: Mapped[str] = mapped_column(String(12), default="de")
    target_language: Mapped[str] = mapped_column(String(12), default="en")
    backend_configuration: Mapped[str] = mapped_column(Text, default="{}")
    review_preferences: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LearningItem(Base):
    __tablename__ = "learning_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    lemma_or_canonical_text: Mapped[str] = mapped_column(String(500))
    original_text: Mapped[str] = mapped_column(String(500), index=True)
    normalized_text: Mapped[str] = mapped_column(String(500), index=True)
    item_type: Mapped[str] = mapped_column(String(20))
    source_language: Mapped[str] = mapped_column(String(12), default="de")
    target_language: Mapped[str] = mapped_column(String(12), default="en")
    translation: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    normalized_translation: Mapped[str] = mapped_column(String(1000), default="")
    article: Mapped[str | None] = mapped_column(String(32), nullable=True)
    plural: Mapped[str | None] = mapped_column(String(500), nullable=True)
    infinitive: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verb_forms: Mapped[str | None] = mapped_column(Text, nullable=True)
    separable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    required_preposition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_case: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    meanings: Mapped[list[Meaning]] = relationship(back_populates="learning_item", cascade="all, delete-orphan")
    occurrences: Mapped[list[Occurrence]] = relationship(back_populates="learning_item", cascade="all, delete-orphan")
    flashcards: Mapped[list[Flashcard]] = relationship(back_populates="learning_item", cascade="all, delete-orphan")


class Meaning(Base):
    __tablename__ = "meanings"
    id: Mapped[int] = mapped_column(primary_key=True)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey("learning_items.id", ondelete="CASCADE"))
    translation: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[str] = mapped_column(String(30), default="unknown")
    learning_item: Mapped[LearningItem] = relationship(back_populates="meanings")


class Occurrence(Base):
    __tablename__ = "occurrences"
    id: Mapped[int] = mapped_column(primary_key=True)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey("learning_items.id", ondelete="CASCADE"))
    selected_text: Mapped[str] = mapped_column(String(500))
    source_sentence: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    page_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_url: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    source_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    video_timestamp_nullable: Mapped[float | None] = mapped_column(Float, nullable=True)
    encountered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    learning_item: Mapped[LearningItem] = relationship(back_populates="occurrences")


class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[int] = mapped_column(primary_key=True)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey("learning_items.id", ondelete="CASCADE"))
    card_type: Mapped[str] = mapped_column(String(30))
    prompt_template: Mapped[str] = mapped_column(Text)
    answer_template: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    learning_item: Mapped[LearningItem] = relationship(back_populates="flashcards")
    review_state: Mapped[ReviewState] = relationship(back_populates="card", cascade="all, delete-orphan", uselist=False)


class ReviewState(Base):
    __tablename__ = "review_states"
    card_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), primary_key=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    interval_days: Mapped[float] = mapped_column(Float, default=0)
    ease_or_difficulty: Mapped[float] = mapped_column(Float, default=2.5)
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)
    lapse_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    card: Mapped[Flashcard] = relationship(back_populates="review_state")


class ReviewEvent(Base):
    __tablename__ = "review_events"
    __table_args__ = (UniqueConstraint("id", "card_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), index=True)
    rating: Mapped[str] = mapped_column(String(10))
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_answer: Mapped[str] = mapped_column(Text)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    was_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    previous_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    new_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
