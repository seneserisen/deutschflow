# Phase 5: Live transcription and translation (planned)

Explicit user action → tab audio capture → local processing/VAD → local German transcription → optional translation → subtitle overlay. A replaceable provider could later wrap `whisper.cpp`; it is not installed or integrated now.

Design work must handle MV3 service-worker suspension, offscreen documents, preserved audio playback, latency/CPU/GPU budgets, unstable partial transcripts, subtitle stabilization, Chrome/Opera differences, an unmistakable capture indicator, and immediate stop controls. No background capture, full-video audio storage, DRM bypass, or guaranteed protected-content support. No Phase 5 code exists yet.

