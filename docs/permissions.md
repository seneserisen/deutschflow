# Extension permissions

| Permission | Reason |
|---|---|
| `activeTab` | Temporary access only after the user invokes the selection context menu |
| `scripting` | One-shot, bounded context extraction on that active page |
| `contextMenus` | Provide “DeutschFlow: Learn selection” only for selections |
| `storage` | Store settings, token, and current pending selection locally |
| `sidePanel` | Display the learning workspace without replacing the webpage |
| `http://127.0.0.1:8765/*` | Call the fixed default loopback companion API |

There is no mandatory `<all_urls>` permission and no history, cookies, webRequest, clipboard read, downloads, microphone, camera, `tabCapture`, or `offscreen` access. Restricted browser pages reject injection by design; only the menu-supplied text remains available.

Later assisted-reading features must use explicit optional site permissions. Audio-related permissions are not present in Phase 1.

