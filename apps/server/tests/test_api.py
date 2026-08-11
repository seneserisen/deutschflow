from datetime import datetime


def test_health_is_public_and_minimal(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["application"] == "deutschflow"
    assert set(response.json()) == {"application", "status", "version", "provider_available"}


def test_authentication_failures_are_structured(client):
    missing = client.get("/api/v1/items")
    invalid = client.get("/api/v1/items", headers={"Authorization": "Bearer wrong"})
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "PAIRING_REQUIRED"
    assert invalid.json()["error"]["code"] == "INVALID_TOKEN"


def test_pairing_flow(client):
    start = client.post("/api/v1/pairing/start")
    code = start.json()["pairing_code"]
    complete = client.post("/api/v1/pairing/complete", json={"code": code})
    assert complete.json() == {"token": "test-token"}


def test_item_creation_duplicate_and_edit(client, auth, item_payload):
    created = client.post("/api/v1/items", headers=auth, json=item_payload)
    assert created.status_code == 201
    body = created.json()
    assert len(body["meanings"]) == 1
    assert len(body["occurrences"]) == 1
    assert {card["card_type"] for card in body["flashcards"]} == {"recognition", "production", "cloze", "article"}

    duplicate = client.post("/api/v1/items", headers=auth, json=item_payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "DUPLICATE_ITEM"

    edited = client.patch(f"/api/v1/items/{body['id']}", headers=auth, json={"notes": "Personal note", "status": "suspended"})
    assert edited.json()["notes"] == "Personal note"
    assert edited.json()["status"] == "suspended"


def test_same_text_can_store_separate_sense(client, auth, item_payload):
    client.post("/api/v1/items", headers=auth, json=item_payload)
    second = {**item_payload, "translation": "practical knowledge", "duplicate_action": "create_new"}
    second["meaning"] = {"translation": "practical knowledge", "context_note": "work context"}
    response = client.post("/api/v1/items", headers=auth, json=second)
    assert response.status_code == 201
    assert response.json()["meanings"][0]["context_note"] == "work context"


def test_search_filters_and_delete(client, auth, item_payload):
    item = client.post("/api/v1/items", headers=auth, json=item_payload).json()
    assert client.get("/api/v1/items?q=erfahrung&source_domain=example.org", headers=auth).json()["count"] == 1
    assert client.delete(f"/api/v1/items/{item['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/items/{item['id']}", headers=auth).status_code == 404


def test_suspended_cards_are_not_due(client, auth, item_payload):
    item = client.post("/api/v1/items", headers=auth, json=item_payload).json()
    assert client.get("/api/v1/review/due", headers=auth).json()["count"] == 4
    client.patch(f"/api/v1/items/{item['id']}", headers=auth, json={"status": "suspended"})
    assert client.get("/api/v1/review/due", headers=auth).json()["count"] == 0


def test_review_updates_due_date_and_preserves_event_in_export(client, auth, item_payload):
    item = client.post("/api/v1/items", headers=auth, json=item_payload).json()
    due = client.get("/api/v1/review/due", headers=auth).json()["cards"]
    response = client.post(f"/api/v1/review/{due[0]['id']}", headers=auth, json={"rating": "good", "response": "experience", "was_correct": True})
    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["new_due_at"]).tzinfo is not None
    exported = client.get("/api/v1/export/json", headers=auth).json()
    assert exported["schema_version"] == 1
    assert exported["data"]["review_events"][0]["rating"] == "good"
    assert exported["data"]["items"][0]["id"] == item["id"]


def test_csv_export(client, auth, item_payload):
    client.post("/api/v1/items", headers=auth, json=item_payload)
    response = client.get("/api/v1/export/csv", headers=auth)
    assert response.status_code == 200
    assert "German,Translation" in response.text
    assert "die Erfahrung,experience" in response.text


def test_import_preview_apply_and_duplicate_skip(client, auth, item_payload):
    source_item = client.post("/api/v1/items", headers=auth, json=item_payload).json()
    client.delete(f"/api/v1/items/{source_item['id']}", headers=auth)
    package = {"schema_version": 1, "exported_at": "2026-01-01T00:00:00Z", "application_version": "0.1.0",
               "data": {"items": [source_item], "review_events": []}, "duplicate_handling": "skip"}
    preview = client.post("/api/v1/import/preview", headers=auth, json=package)
    assert preview.json()["will_create"] == 1
    assert client.post("/api/v1/import/apply", headers=auth, json=package).json()["created"] == 1
    assert client.post("/api/v1/import/apply", headers=auth, json=package).json()["created"] == 0


def test_import_restores_review_state_and_history_transactionally(client, auth, item_payload):
    client.post("/api/v1/items", headers=auth, json=item_payload)
    card = client.get("/api/v1/review/due", headers=auth).json()["cards"][0]
    client.post(f"/api/v1/review/{card['id']}", headers=auth, json={"rating": "hard"})
    package = client.get("/api/v1/export/json", headers=auth).json()
    package["duplicate_handling"] = "skip"
    client.delete("/api/v1/data", headers=auth)
    assert client.get("/api/v1/export/json", headers=auth).json()["data"]["review_events"] == []
    applied = client.post("/api/v1/import/apply", headers=auth, json=package)
    assert applied.status_code == 200
    restored = client.get("/api/v1/export/json", headers=auth).json()
    assert restored["data"]["review_events"][0]["rating"] == "hard"
    states = restored["data"]["items"][0]["flashcards"]
    assert any(card["review_state"]["repetition_count"] == 1 for card in states)


def test_malformed_import_does_not_change_database(client, auth):
    package = {"schema_version": 1, "exported_at": "2026-01-01T00:00:00Z", "application_version": "0.1.0",
               "data": {"items": [{"original_text": "Hallo", "item_type": "invalid"}]}}
    assert client.post("/api/v1/import/apply", headers=auth, json=package).status_code == 422
    assert client.get("/api/v1/items", headers=auth).json()["count"] == 0


def test_selection_validation_and_translation(client, auth):
    blank = client.post("/api/v1/translate", headers=auth, json={"text": "   "})
    assert blank.status_code == 422
    translated = client.post("/api/v1/translate", headers=auth, json={"text": "Hallo", "source_language": "de", "target_language": "en"})
    assert translated.json()["translated_text"] == "hello"


def test_request_size_limit(client, auth):
    response = client.post("/api/v1/import/preview", headers={**auth, "content-length": "1000001"}, content=b"{}")
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_TOO_LARGE"
