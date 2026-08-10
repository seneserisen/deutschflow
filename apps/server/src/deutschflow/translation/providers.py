from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderHealth:
    available: bool
    detail: str


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str
    source_language: str
    target_language: str
    provider_name: str
    provider_version: str | None = None
    model_or_package: str | None = None
    confidence_or_unknown: str = "unknown"
    warnings: tuple[str, ...] = ()


class TranslationProvider(Protocol):
    name: str
    def health(self) -> ProviderHealth: ...
    def supported_pairs(self) -> set[tuple[str, str]]: ...
    def translate(self, text: str, source: str, target: str) -> TranslationResult: ...


class ProviderUnavailable(RuntimeError):
    pass


class LanguagePairUnavailable(RuntimeError):
    pass


class DisabledProvider:
    name = "disabled"
    def health(self) -> ProviderHealth:
        return ProviderHealth(False, "Install and configure a local translation provider.")
    def supported_pairs(self) -> set[tuple[str, str]]:
        return set()
    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        raise ProviderUnavailable(self.health().detail)


class FakeProvider:
    name = "fake"
    _translations = {"hallo": "hello", "guten morgen": "good morning", "lernen": "to learn"}
    def health(self) -> ProviderHealth:
        return ProviderHealth(True, "Development-only deterministic provider")
    def supported_pairs(self) -> set[tuple[str, str]]:
        return {("de", "en")}
    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        if (source, target) not in self.supported_pairs():
            raise LanguagePairUnavailable(f"{source} to {target} is unavailable")
        translated = self._translations.get(text.casefold(), f"[test] {text}")
        return TranslationResult(translated, source, target, self.name, "1", "fixture")


class ArgosProvider:
    name = "argos"
    def _module(self):
        try:
            import argostranslate.package as package  # type: ignore[import-not-found]
            import argostranslate.translate as translate  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ProviderUnavailable("Argos Translate is not installed. See README model setup.") from exc
        return package, translate

    def _languages(self):
        _, translate = self._module()
        return translate.get_installed_languages()

    def supported_pairs(self) -> set[tuple[str, str]]:
        try:
            languages = self._languages()
        except ProviderUnavailable:
            return set()
        pairs: set[tuple[str, str]] = set()
        for source in languages:
            for target in languages:
                if source.code != target.code:
                    try:
                        if source.get_translation(target) is not None:
                            pairs.add((source.code, target.code))
                    except Exception:
                        pass
        return pairs

    def health(self) -> ProviderHealth:
        try:
            pairs = self.supported_pairs()
        except Exception as exc:
            return ProviderHealth(False, f"Argos inspection failed: {type(exc).__name__}")
        if not pairs:
            return ProviderHealth(False, "Argos is installed but has no usable local language packages.")
        return ProviderHealth(True, f"{len(pairs)} local language pair(s) available")

    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        if (source, target) not in self.supported_pairs():
            raise LanguagePairUnavailable(f"No installed Argos package supports {source} to {target}.")
        languages = {language.code: language for language in self._languages()}
        translation = languages[source].get_translation(languages[target])
        result = translation.translate(text)
        return TranslationResult(result, source, target, self.name, model_or_package=f"{source}-{target}")


def get_provider(name: str) -> TranslationProvider:
    if name == "fake":
        return FakeProvider()
    if name == "argos":
        return ArgosProvider()
    return DisabledProvider()
