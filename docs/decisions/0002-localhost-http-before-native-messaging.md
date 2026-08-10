# ADR 0002: Loopback HTTP before Native Messaging

Status: accepted

Phase 1 uses a versioned JSON API bound to `127.0.0.1`. Requests to protected routes carry a locally generated bearer token. This is easier to install and test than Native Messaging while retaining a replaceable transport boundary.

The service is not designed for internet exposure. Native Messaging may be reconsidered for packaging after the learning workflow is validated.

