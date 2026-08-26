# Security Policy

## Supported Versions

FRAME is currently an experimental prototype under active development.

Security fixes are applied to the latest version on the `main` branch.

| Version                   | Supported |
| ------------------------- | --------- |
| `main`                    | ✅        |
| Older commits / snapshots | ❌        |

---

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security-sensitive vulnerabilities.

Instead, report the issue privately to the project maintainer.

When reporting a vulnerability, please include:

- a clear description of the issue
- affected component or endpoint
- reproduction steps
- expected behavior
- actual behavior
- potential impact
- proof of concept, if available
- suggested mitigation, if known

Please avoid including real payment credentials, personal data, authentication secrets, or other sensitive information in reports.

---

## Security Scope

Security-relevant areas in FRAME include:

- API input validation
- transaction replay and duplicate handling
- out-of-order event handling
- concurrency and shared in-memory state
- graph serialization
- model artifact loading
- frontend/backend API boundaries
- analyst investigation data exposure
- dependency vulnerabilities

---

## Model Artifact Safety

FRAME currently loads a locally generated model artifact for inference.

Serialized Python model artifacts should be treated as trusted local files.

Do not load untrusted or externally supplied serialized model files.

Python serialization formats such as `pickle` can execute arbitrary code during deserialization.

---

## Runtime State

FRAME currently stores its online graph, temporal state, scored results, and transaction context in memory.

This means:

- state is reset when the backend restarts
- runtime state is not currently persisted
- the prototype should not be treated as a durable transaction ledger
- multiple independent server processes do not share scoring state

---

## Public API Boundaries

The public scoring API intentionally excludes training and evaluation labels such as:

- `is_fraud`
- `fraud_ring_id`

These values are used only for synthetic generation and evaluation and are not accepted as scoring inputs.

FRAME also rejects:

- duplicate transaction IDs
- out-of-order transaction timestamps

These protections help prevent accidental corruption of the stateful online feature pipeline.

---

## Data Privacy

FRAME's current benchmark and demo use synthetic data.

Do not use real payment, customer, card, IP, or identity data without appropriate authorization, security controls, and privacy protections.

Real-world deployment would require additional controls including:

- authentication and authorization
- encryption in transit and at rest
- secure secret management
- access logging
- audit trails
- data retention policies
- privacy review
- regulatory and compliance review

---

## Security Limitations

FRAME is not currently presented as a production-ready fraud detection or payment authorization system.

The current project does not yet provide production-grade:

- authentication
- authorization
- persistent storage
- distributed state coordination
- secrets management
- rate limiting
- audit logging
- encrypted data storage
- deployment hardening

These limitations should be considered before any use beyond experimentation or demonstration.

---

## Responsible Disclosure

Please allow reasonable time for investigation and remediation before publicly disclosing a vulnerability.

Good-faith security research and responsible disclosure are appreciated.

---

## License

This project is licensed under the MIT License.
