def test_complete_learning_loop(client, auth):
    translation = client.post("/api/v1/translate", headers=auth, json={"text": "lernen", "context": "Wir lernen Deutsch."}).json()
    item = client.post("/api/v1/items", headers=auth, json={
        "original_text": "lernen", "item_type": "word", "translation": translation["translated_text"],
        "occurrence": {"selected_text": "lernen", "source_sentence": "Wir lernen Deutsch.",
                       "page_title": "Fixture", "page_url": "https://example.test", "source_domain": "example.test"},
        "meaning": {"translation": translation["translated_text"], "provider": translation["provider_name"], "confidence": "unknown"},
    }).json()
    assert {card["card_type"] for card in item["flashcards"]} == {"recognition", "production", "cloze"}
    due = client.get("/api/v1/review/due", headers=auth).json()["cards"]
    review = client.post(f"/api/v1/review/{due[0]['id']}", headers=auth, json={"rating": "easy"})
    assert review.json()["interval_days"] == 4
    exported = client.get("/api/v1/export/json", headers=auth).json()
    assert exported["data"]["items"][0]["original_text"] == "lernen"
    assert len(exported["data"]["review_events"]) == 1

