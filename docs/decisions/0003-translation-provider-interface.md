# ADR 0003: Translation provider interface

Status: accepted

Translation is behind a provider protocol exposing health, supported pairs, and translation. `ArgosProvider` detects already-installed Argos packages but never downloads them. `DisabledProvider` returns an actionable unavailable state. `FakeProvider` is enabled only by an explicit development/test setting.

Future local-LLM, user-configured remote, browser-native, dictionary, and morphology providers remain planned only.

