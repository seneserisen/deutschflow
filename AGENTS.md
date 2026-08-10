# DeutschFlow repository instructions

- Read the relevant files in `docs/` before changing behavior.
- Preserve the boundary between `apps/extension` and `apps/server`; communicate only through the documented local API.
- Keep extension permissions minimal and treat all webpage text, titles, and URLs as untrusted input.
- Never render webpage-provided HTML or log complete selected content by default.
- Never add telemetry, remote translation fallbacks, or hard-coded secrets.
- Never download translation models automatically, including during tests.
- Do not invent translation-quality, language-learning, or scheduling-effectiveness claims.
- Add behavior-focused tests for changes and preserve JSON import/export compatibility.
- Document schema or API changes in `docs/data_model.md` and `docs/api.md`.
- Do not modify other repositories or portfolio-planning files.
- Do not commit, push, publish, deploy, or create a remote without explicit approval.
- Review the complete diff plus permission, secret, unsafe-HTML, and fake-provider usage before handoff.

