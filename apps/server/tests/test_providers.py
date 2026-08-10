import pytest

from deutschflow.translation.providers import (
    ArgosProvider,
    DisabledProvider,
    FakeProvider,
    LanguagePairUnavailable,
    ProviderUnavailable,
)


def test_fake_provider_is_deterministic():
    provider = FakeProvider()
    assert provider.translate("Hallo", "de", "en").translated_text == "hello"


def test_fake_provider_rejects_unsupported_pair():
    with pytest.raises(LanguagePairUnavailable):
        FakeProvider().translate("Hallo", "de", "tr")


def test_disabled_provider_never_fabricates_translation():
    provider = DisabledProvider()
    assert not provider.health().available
    with pytest.raises(ProviderUnavailable):
        provider.translate("Hallo", "de", "en")


def test_argos_reports_missing_adapter_without_downloading(monkeypatch):
    provider = ArgosProvider()
    monkeypatch.setattr(provider, "_module", lambda: (_ for _ in ()).throw(ProviderUnavailable("not installed")))
    assert provider.supported_pairs() == set()
    assert provider.health().available is False
