from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deutschflow.config import Settings
from deutschflow.main import create_app
from deutschflow.translation.providers import FakeProvider


@pytest.fixture
def client(tmp_path: Path):
    config = Settings(data_dir=tmp_path, database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}", provider="fake")
    app = create_app(config, provider=FakeProvider(), token="test-token")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def item_payload():
    return {
        "original_text": "die Erfahrung",
        "item_type": "phrase",
        "translation": "experience",
        "article": "die",
        "occurrence": {
            "selected_text": "die Erfahrung",
            "source_sentence": "Die Erfahrung war sehr hilfreich.",
            "page_title": "Beispiel",
            "page_url": "https://example.org/lernen",
            "source_domain": "example.org",
        },
        "meaning": {"translation": "experience", "provider": "fake", "confidence": "unknown"},
    }
