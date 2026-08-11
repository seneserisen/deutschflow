from __future__ import annotations

import csv
import io
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from deutschflow import __version__
from deutschflow.config import Settings, settings
from deutschflow.db.database import Base, build_engine
from deutschflow.models import (
    AppSetting,
    Flashcard,
    LearningItem,
    Meaning,
    Occurrence,
    ReviewEvent,
    ReviewState,
)
from deutschflow.models.entities import utcnow
from deutschflow.review.scheduler import schedule_review
from deutschflow.schemas.api import (
    ImportRequest,
    ItemCreate,
    ItemPatch,
    PairingComplete,
    ReviewSubmission,
    TranslateRequest,
)
from deutschflow.translation.providers import (
    LanguagePairUnavailable,
    ProviderUnavailable,
    TranslationProvider,
    get_provider,
)

logger = logging.getLogger("deutschflow")


def normalize(value: str | None) -> str:
    return " ".join((value or "").split()).casefold()


def error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def item_dict(item: LearningItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "lemma_or_canonical_text": item.lemma_or_canonical_text,
        "original_text": item.original_text,
        "item_type": item.item_type,
        "source_language": item.source_language,
        "target_language": item.target_language,
        "translation": item.translation,
        "article": item.article,
        "plural": item.plural,
        "infinitive": item.infinitive,
        "verb_forms": item.verb_forms,
        "separable": item.separable,
        "required_preposition": item.required_preposition,
        "required_case": item.required_case,
        "notes": item.notes,
        "topic": item.topic,
        "status": item.status,
        "created_at": iso(item.created_at),
        "updated_at": iso(item.updated_at),
        "meanings": [
            {"id": m.id, "translation": m.translation, "definition": m.definition, "context_note": m.context_note,
             "provider": m.provider, "confidence": m.confidence}
            for m in item.meanings
        ],
        "occurrences": [
            {"id": o.id, "selected_text": o.selected_text, "source_sentence": o.source_sentence,
             "page_title": o.page_title, "page_url": o.page_url, "source_domain": o.source_domain,
             "video_timestamp_nullable": o.video_timestamp_nullable, "encountered_at": iso(o.encountered_at)}
            for o in item.occurrences
        ],
        "flashcards": [
            {"id": c.id, "card_type": c.card_type, "prompt_template": c.prompt_template,
             "answer_template": c.answer_template, "enabled": c.enabled,
             "review_state": None if c.review_state is None else {
                 "due_at": iso(c.review_state.due_at), "interval_days": c.review_state.interval_days,
                 "ease_or_difficulty": c.review_state.ease_or_difficulty,
                 "repetition_count": c.review_state.repetition_count,
                 "lapse_count": c.review_state.lapse_count,
                 "last_reviewed_at": iso(c.review_state.last_reviewed_at),
             }} for c in item.flashcards
        ],
    }


def load_item(session: Session, item_id: int) -> LearningItem | None:
    return session.scalar(
        select(LearningItem).where(LearningItem.id == item_id).options(
            selectinload(LearningItem.meanings), selectinload(LearningItem.occurrences),
            selectinload(LearningItem.flashcards).selectinload(Flashcard.review_state),
        )
    )


def create_cards(item: LearningItem, now: datetime, requested: list[str] | None = None) -> None:
    requested = requested or ["recognition", "production", "cloze", "article"]
    definitions = []
    if "recognition" in requested and item.translation:
        definitions.append(("recognition", "{{german}}", "{{translation}}"))
    if "production" in requested and item.translation:
        definitions.append(("production", "{{translation}}", "{{german}}"))
    sentence = item.occurrences[0].source_sentence if item.occurrences else None
    if "cloze" in requested and sentence and item.original_text.casefold() in sentence.casefold():
        definitions.append(("cloze", "{{cloze_sentence}}", "{{german}}"))
    if "article" in requested and item.article:
        definitions.append(("article", "Article: {{german_without_article}}", "{{article}}"))
    if "source_sentence" in requested and sentence and item.original_text.casefold() in sentence.casefold():
        definitions.append(("source_sentence", "{{source_sentence_with_gap}}", "{{german}}"))
    for card_type, prompt, answer in definitions:
        card = Flashcard(card_type=card_type, prompt_template=prompt, answer_template=answer)
        card.review_state = ReviewState(due_at=now)
        item.flashcards.append(card)


def create_app(
    config: Settings | None = None,
    *,
    database_url: str | None = None,
    provider: TranslationProvider | None = None,
    token: str | None = None,
) -> FastAPI:
    cfg = config or settings
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    local_engine = build_engine(database_url or cfg.db_url)
    sessions = sessionmaker(bind=local_engine, expire_on_commit=False)
    Base.metadata.create_all(local_engine)
    with sessionmaker(bind=local_engine)() as initialization_session:
        if initialization_session.get(AppSetting, 1) is None:
            initialization_session.add(AppSetting(id=1))
            initialization_session.commit()
    chosen_provider = provider or get_provider(cfg.provider)

    token_path = cfg.data_dir / "api.token"
    if token is None:
        if token_path.exists():
            token = token_path.read_text(encoding="utf-8").strip()
        else:
            token = secrets.token_urlsafe(32)
            token_path.write_text(token, encoding="utf-8")
    api_token = token
    pairing: dict[str, Any] = {}

    app = FastAPI(title="DeutschFlow local API", version=__version__)
    app.state.database_url = database_url or cfg.db_url
    app.state.provider = chosen_provider
    app.state.api_token = api_token
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cfg.cors_origins.split(",") if origin.strip()],
        allow_origin_regex=r"^chrome-extension://[a-z]{32}$",
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def limit_body(request: Request, call_next):
        raw_length = request.headers.get("content-length")
        if raw_length and int(raw_length) > cfg.max_body_bytes:
            return JSONResponse(status_code=413, content={"error": {"code": "REQUEST_TOO_LARGE", "message": "Request body is too large."}})
        return await call_next(request)

    @app.exception_handler(HTTPException)
    async def structured_error(_request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, dict) else {"code": "HTTP_ERROR", "message": str(exc.detail)}
        return JSONResponse(status_code=exc.status_code, content={"error": detail})

    def db():
        with sessions() as session:
            yield session

    def authenticate(authorization: str | None = Header(default=None)) -> None:
        if not authorization:
            raise error(401, "PAIRING_REQUIRED", "Pair the extension with the local service.")
        scheme, _, candidate = authorization.partition(" ")
        if scheme.casefold() != "bearer" or not secrets.compare_digest(candidate, api_token):
            raise error(401, "INVALID_TOKEN", "The local API token is invalid.")

    @app.get("/api/v1/health")
    def health():
        status = chosen_provider.health()
        return {
            "application": "deutschflow",
            "status": "ok",
            "version": __version__,
            "provider_available": status.available,
        }

    @app.post("/api/v1/pairing/start")
    def pairing_start(request: Request):
        if request.client and request.client.host not in {"127.0.0.1", "::1", "testclient"}:
            raise error(403, "LOOPBACK_ONLY", "Pairing is available only on this computer.")
        code = f"{secrets.randbelow(1_000_000):06d}"
        pairing.update(code=code, expires=utcnow() + timedelta(minutes=5))
        logger.info("DeutschFlow pairing code: %s (valid for five minutes)", code)
        return {"pairing_code": code, "expires_at": iso(pairing["expires"])}

    @app.post("/api/v1/pairing/complete")
    def pairing_complete(payload: PairingComplete):
        expires = pairing.get("expires")
        if not expires or utcnow() > expires or not secrets.compare_digest(payload.code, pairing.get("code", "")):
            raise error(400, "PAIRING_CODE_INVALID", "Pairing code is invalid or expired.")
        pairing.clear()
        return {"token": api_token}

    @app.get("/api/v1/providers", dependencies=[Depends(authenticate)])
    def providers():
        status = chosen_provider.health()
        return [{"name": chosen_provider.name, "available": status.available, "detail": status.detail,
                 "supported_pairs": sorted([list(pair) for pair in chosen_provider.supported_pairs()])}]

    @app.post("/api/v1/translate", dependencies=[Depends(authenticate)])
    def translate(payload: TranslateRequest):
        if len(payload.text) > cfg.max_selection_length:
            raise error(422, "SELECTION_TOO_LONG", f"Selection exceeds {cfg.max_selection_length} characters.")
        try:
            result = chosen_provider.translate(payload.text, payload.source_language, payload.target_language)
        except ProviderUnavailable as exc:
            raise error(503, "TRANSLATION_PROVIDER_UNAVAILABLE", str(exc)) from exc
        except LanguagePairUnavailable as exc:
            raise error(422, "LANGUAGE_PAIR_UNAVAILABLE", str(exc)) from exc
        return result.__dict__

    @app.post("/api/v1/items", dependencies=[Depends(authenticate)], status_code=201)
    def add_item(payload: ItemCreate, session: Session = Depends(db)):
        normalized_text, normalized_translation = normalize(payload.original_text), normalize(payload.translation)
        duplicate = session.scalar(select(LearningItem).where(
            LearningItem.normalized_text == normalized_text,
            LearningItem.normalized_translation == normalized_translation,
        ).order_by(LearningItem.id))
        if duplicate and payload.duplicate_action == "reject":
            raise error(409, "DUPLICATE_ITEM", f"Exact item already exists as #{duplicate.id}.")
        if duplicate and payload.duplicate_action == "attach_occurrence":
            if not payload.occurrence:
                raise error(422, "OCCURRENCE_REQUIRED", "An occurrence is required to attach to an existing item.")
            duplicate.occurrences.append(Occurrence(**payload.occurrence.model_dump(mode="json")))
            session.commit()
            return item_dict(load_item(session, duplicate.id))
        fields = payload.model_dump(exclude={"occurrence", "meaning", "duplicate_action", "card_types"})
        fields["lemma_or_canonical_text"] = fields["lemma_or_canonical_text"] or payload.original_text
        fields.update(normalized_text=normalized_text, normalized_translation=normalized_translation)
        item = LearningItem(**fields)
        if payload.occurrence:
            occurrence_data = payload.occurrence.model_dump(mode="json")
            if occurrence_data.get("page_url") is not None:
                occurrence_data["page_url"] = str(occurrence_data["page_url"])
            item.occurrences.append(Occurrence(**occurrence_data))
        if payload.meaning or payload.translation:
            meaning = payload.meaning or None
            item.meanings.append(Meaning(**(meaning.model_dump() if meaning else {"translation": payload.translation})))
        create_cards(item, utcnow(), payload.card_types)
        session.add(item)
        session.commit()
        return item_dict(load_item(session, item.id))

    @app.get("/api/v1/items", dependencies=[Depends(authenticate)])
    def list_items(
        q: str | None = None, status: str | None = None, item_type: str | None = None,
        source_domain: str | None = None, review_state: str | None = None,
        session: Session = Depends(db),
    ):
        statement = select(LearningItem).options(
            selectinload(LearningItem.meanings), selectinload(LearningItem.occurrences),
            selectinload(LearningItem.flashcards).selectinload(Flashcard.review_state),
        )
        if q:
            query = f"%{normalize(q)}%"
            statement = statement.where(or_(LearningItem.normalized_text.like(query), LearningItem.normalized_translation.like(query)))
        if status:
            statement = statement.where(LearningItem.status == status)
        if item_type:
            statement = statement.where(LearningItem.item_type == item_type)
        if source_domain:
            statement = statement.join(LearningItem.occurrences).where(Occurrence.source_domain == source_domain)
        if review_state == "due":
            statement = statement.join(LearningItem.flashcards).join(Flashcard.review_state).where(ReviewState.due_at <= utcnow())
        if review_state == "suspended":
            statement = statement.where(LearningItem.status == "suspended")
        items = session.scalars(statement.order_by(LearningItem.created_at.desc())).unique().all()
        return {"items": [item_dict(item) for item in items], "count": len(items)}

    @app.get("/api/v1/items/{item_id}", dependencies=[Depends(authenticate)])
    def get_item(item_id: int, session: Session = Depends(db)):
        item = load_item(session, item_id)
        if not item:
            raise error(404, "ITEM_NOT_FOUND", "Learning item not found.")
        return item_dict(item)

    @app.patch("/api/v1/items/{item_id}", dependencies=[Depends(authenticate)])
    def patch_item(item_id: int, payload: ItemPatch, session: Session = Depends(db)):
        item = load_item(session, item_id)
        if not item:
            raise error(404, "ITEM_NOT_FOUND", "Learning item not found.")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        if "translation" in payload.model_fields_set:
            item.normalized_translation = normalize(payload.translation)
        session.commit()
        return item_dict(load_item(session, item_id))

    @app.delete("/api/v1/items/{item_id}", dependencies=[Depends(authenticate)], status_code=204)
    def delete_item(item_id: int, session: Session = Depends(db)):
        item = session.get(LearningItem, item_id)
        if not item:
            raise error(404, "ITEM_NOT_FOUND", "Learning item not found.")
        session.delete(item)
        session.commit()
        return Response(status_code=204)

    @app.get("/api/v1/review/due", dependencies=[Depends(authenticate)])
    def due_cards(limit: int = Query(default=50, ge=1, le=200), session: Session = Depends(db)):
        cards = session.scalars(
            select(Flashcard).join(Flashcard.review_state).join(Flashcard.learning_item)
            .where(Flashcard.enabled.is_(True), LearningItem.status != "suspended", ReviewState.due_at <= utcnow())
            .options(selectinload(Flashcard.review_state), selectinload(Flashcard.learning_item).selectinload(LearningItem.occurrences))
            .order_by(ReviewState.due_at, Flashcard.id).limit(limit)
        ).all()
        result = []
        for card in cards:
            item = card.learning_item
            result.append({"id": card.id, "card_type": card.card_type, "german": item.original_text,
                           "translation": item.translation, "article": item.article,
                           "source_sentence": item.occurrences[0].source_sentence if item.occurrences else None,
                           "due_at": iso(card.review_state.due_at)})
        return {"cards": result, "count": len(result)}

    @app.post("/api/v1/review/{card_id}", dependencies=[Depends(authenticate)])
    def review(card_id: int, payload: ReviewSubmission, session: Session = Depends(db)):
        card = session.scalar(select(Flashcard).where(Flashcard.id == card_id).options(
            selectinload(Flashcard.review_state), selectinload(Flashcard.learning_item)))
        if not card or not card.review_state:
            raise error(404, "CARD_NOT_FOUND", "Flashcard not found.")
        state, now = card.review_state, utcnow()
        previous_due = state.due_at
        next_state = schedule_review(rating=payload.rating, interval_days=state.interval_days,
                                     ease=state.ease_or_difficulty, repetitions=state.repetition_count,
                                     lapses=state.lapse_count, now=now)
        state.due_at, state.interval_days = next_state.due_at, next_state.interval_days
        state.ease_or_difficulty, state.repetition_count = next_state.ease, next_state.repetitions
        state.lapse_count, state.last_reviewed_at = next_state.lapses, now
        expected = card.learning_item.translation if card.card_type == "recognition" else card.learning_item.original_text
        session.add(ReviewEvent(card_id=card.id, rating=payload.rating, response=payload.response,
                                expected_answer=expected or "", response_time_ms=payload.response_time_ms,
                                was_correct=payload.was_correct, reviewed_at=now,
                                previous_due_at=previous_due, new_due_at=next_state.due_at))
        if card.learning_item.status == "new":
            card.learning_item.status = "learning"
        session.commit()
        return {"card_id": card.id, "new_due_at": iso(next_state.due_at), "interval_days": next_state.interval_days}

    def export_payload(session: Session) -> dict[str, Any]:
        items = session.scalars(select(LearningItem).options(
            selectinload(LearningItem.meanings), selectinload(LearningItem.occurrences),
            selectinload(LearningItem.flashcards).selectinload(Flashcard.review_state))).all()
        events = session.scalars(select(ReviewEvent).order_by(ReviewEvent.id)).all()
        local_settings = session.get(AppSetting, 1)
        return {"schema_version": 1, "exported_at": iso(utcnow()), "application_version": __version__,
                "data": {"settings": {
                    "source_language": local_settings.source_language if local_settings else "de",
                    "target_language": local_settings.target_language if local_settings else "en",
                    "review_preferences": local_settings.review_preferences if local_settings else "{}",
                },
                         "items": [item_dict(item) for item in items],
                         "review_events": [{"id": event.id, "card_id": event.card_id, "rating": event.rating,
                            "response": event.response, "expected_answer": event.expected_answer,
                            "response_time_ms": event.response_time_ms, "was_correct": event.was_correct,
                            "reviewed_at": iso(event.reviewed_at), "previous_due_at": iso(event.previous_due_at),
                            "new_due_at": iso(event.new_due_at)} for event in events]}}

    @app.get("/api/v1/export/json", dependencies=[Depends(authenticate)])
    def export_json(session: Session = Depends(db)):
        return export_payload(session)

    @app.get("/api/v1/export/csv", dependencies=[Depends(authenticate)])
    def export_csv(session: Session = Depends(db)):
        items = session.scalars(select(LearningItem).options(
            selectinload(LearningItem.occurrences), selectinload(LearningItem.flashcards).selectinload(Flashcard.review_state))).all()
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["German", "Translation", "Article", "Plural", "Type", "Example", "Topic", "Status", "Next Review", "Source URL"])
        for item in items:
            occurrence = item.occurrences[0] if item.occurrences else None
            dates = [c.review_state.due_at for c in item.flashcards if c.review_state]
            writer.writerow([item.original_text, item.translation or "", item.article or "", item.plural or "", item.item_type,
                             occurrence.source_sentence if occurrence else "", item.topic or "", item.status,
                             iso(min(dates)) if dates else "", occurrence.page_url if occurrence else ""])
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv; charset=utf-8",
                                 headers={"Content-Disposition": "attachment; filename=deutschflow-vocabulary.csv"})

    def validate_import(payload: ImportRequest, session: Session) -> dict[str, Any]:
        items = payload.data.get("items")
        if not isinstance(items, list):
            raise error(422, "IMPORT_MALFORMED", "data.items must be an array.")
        malformed = [index for index, item in enumerate(items) if not isinstance(item, dict) or not item.get("original_text") or item.get("item_type") not in {"word", "phrase", "sentence"}]
        if malformed:
            raise error(422, "IMPORT_MALFORMED", f"Malformed item indexes: {malformed[:10]}")
        duplicate_count = 0
        for item in items:
            if session.scalar(select(func.count()).select_from(LearningItem).where(
                LearningItem.normalized_text == normalize(item.get("original_text")),
                LearningItem.normalized_translation == normalize(item.get("translation")))):
                duplicate_count += 1
        return {"schema_version": 1, "item_count": len(items), "duplicate_count": duplicate_count,
                "will_create": len(items) - duplicate_count if payload.duplicate_handling == "skip" else len(items)}

    @app.post("/api/v1/import/preview", dependencies=[Depends(authenticate)])
    def import_preview(payload: ImportRequest, session: Session = Depends(db)):
        return validate_import(payload, session)

    @app.post("/api/v1/import/apply", dependencies=[Depends(authenticate)])
    def import_apply(payload: ImportRequest, session: Session = Depends(db)):
        preview = validate_import(payload, session)
        created = 0
        card_id_map: dict[int, int] = {}
        try:
            for source in payload.data["items"]:
                exists = session.scalar(select(LearningItem.id).where(
                    LearningItem.normalized_text == normalize(source["original_text"]),
                    LearningItem.normalized_translation == normalize(source.get("translation"))))
                if exists and payload.duplicate_handling == "skip":
                    continue
                item = LearningItem(
                    lemma_or_canonical_text=source.get("lemma_or_canonical_text") or source["original_text"],
                    original_text=source["original_text"], normalized_text=normalize(source["original_text"]),
                    item_type=source["item_type"], source_language=source.get("source_language", "de"),
                    target_language=source.get("target_language", "en"), translation=source.get("translation"),
                    normalized_translation=normalize(source.get("translation")), article=source.get("article"),
                    plural=source.get("plural"), infinitive=source.get("infinitive"), verb_forms=source.get("verb_forms"),
                    separable=source.get("separable"), required_preposition=source.get("required_preposition"),
                    required_case=source.get("required_case"), notes=source.get("notes"), topic=source.get("topic"),
                    status=source.get("status", "new"),
                )
                for occurrence in source.get("occurrences", []):
                    item.occurrences.append(Occurrence(selected_text=occurrence.get("selected_text", source["original_text"]),
                        source_sentence=occurrence.get("source_sentence"), page_title=occurrence.get("page_title"),
                        page_url=occurrence.get("page_url"), source_domain=occurrence.get("source_domain")))
                for meaning in source.get("meanings", []):
                    item.meanings.append(Meaning(translation=meaning.get("translation"), definition=meaning.get("definition"),
                        context_note=meaning.get("context_note"), provider=meaning.get("provider"), confidence=meaning.get("confidence", "unknown")))
                session.add(item)
                session.flush()
                imported_cards = source.get("flashcards", [])
                if imported_cards:
                    for source_card in imported_cards:
                        card = Flashcard(
                            learning_item_id=item.id,
                            card_type=source_card["card_type"],
                            prompt_template=source_card.get("prompt_template", "{{german}}"),
                            answer_template=source_card.get("answer_template", "{{translation}}"),
                            enabled=source_card.get("enabled", True),
                        )
                        source_state = source_card.get("review_state")
                        if source_state:
                            card.review_state = ReviewState(
                                due_at=datetime.fromisoformat(source_state["due_at"]),
                                interval_days=source_state.get("interval_days", 0),
                                ease_or_difficulty=source_state.get("ease_or_difficulty", 2.5),
                                repetition_count=source_state.get("repetition_count", 0),
                                lapse_count=source_state.get("lapse_count", 0),
                                last_reviewed_at=(datetime.fromisoformat(source_state["last_reviewed_at"])
                                                  if source_state.get("last_reviewed_at") else None),
                            )
                        item.flashcards.append(card)
                        session.flush()
                        if source_card.get("id") is not None:
                            card_id_map[int(source_card["id"])] = card.id
                else:
                    create_cards(item, utcnow())
                created += 1
            for source_event in payload.data.get("review_events", []):
                new_card_id = card_id_map.get(int(source_event.get("card_id", -1)))
                if not new_card_id:
                    continue
                session.add(ReviewEvent(
                    card_id=new_card_id, rating=source_event["rating"],
                    response=source_event.get("response"), expected_answer=source_event.get("expected_answer", ""),
                    response_time_ms=source_event.get("response_time_ms"), was_correct=source_event.get("was_correct"),
                    reviewed_at=datetime.fromisoformat(source_event["reviewed_at"]),
                    previous_due_at=datetime.fromisoformat(source_event["previous_due_at"]),
                    new_due_at=datetime.fromisoformat(source_event["new_due_at"]),
                ))
            session.commit()
        except Exception:
            session.rollback()
            raise error(422, "IMPORT_FAILED", "Import validation failed; no records were changed.") from None
        return {**preview, "created": created}

    @app.delete("/api/v1/data", dependencies=[Depends(authenticate)], status_code=204)
    def delete_all(session: Session = Depends(db)):
        for item in session.scalars(select(LearningItem)).all():
            session.delete(item)
        session.commit()
        return Response(status_code=204)

    return app


app = create_app()


def run() -> None:
    if settings.host not in {"127.0.0.1", "::1", "localhost"}:
        raise RuntimeError("DeutschFlow refuses to bind to a non-loopback host")
    uvicorn.run("deutschflow.main:app", host=settings.host, port=settings.port, reload=False)
