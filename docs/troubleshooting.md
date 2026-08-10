# Troubleshooting

## Guided environment diagnosis

Run `DOCTOR.bat` on Windows or `./doctor.sh` on Linux/macOS. Fix entries marked `ERROR`; entries marked `WARN` are informational and do not prevent normal runtime use. The doctor does not install software or modify Git configuration.

## Backend unavailable

Run `RUN.bat` (or `.\scripts\dev-server.ps1` for direct developer use), verify `http://127.0.0.1:8765/api/v1/health`, then use Settings → Check backend. A changed port is not covered by the default manifest host permission.

## Pairing required or invalid token

Use Start pairing and Complete pairing again. The six-digit code expires after five minutes. Deleting browser extension storage also deletes its copy of the token, not the service token.

## Provider needs setup

This is expected without Argos and a compatible installed package. Saving/review remains available. Install the optional adapter/package explicitly and restart; DeutschFlow never downloads it.

## No source sentence

Browser-internal pages and extension galleries block injection. Some DOM selections also lack a useful nearby block. The exact selected text is still retained and no false sentence is invented.

## Side panel does not open in Opera

DeutschFlow should open its packaged panel in a new extension tab. Confirm popups/tabs are permitted and reload the unpacked extension after rebuilding.

## Database reset

Prefer Settings → Delete all learning data. With the server stopped, removing `~/.deutschflow/deutschflow.db` resets learning data; removing `api.token` also requires re-pairing. Export first if recovery matters.
