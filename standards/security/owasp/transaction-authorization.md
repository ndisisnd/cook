---
description: Enforce server-side transaction authorization with WYSIWYS, unique credentials, and replay/downgrade protection
alwaysApply: false
---

# Transaction Authorization

Applies to any sensitive operation requiring explicit user consent: wire transfers, privilege changes, account unlocks, data modifications.

## NEVER
- Perform authorization checks client-side or allow client to influence authorization results
- Reuse authentication credentials for transaction authorization
- Allow authorization method parameters to be manipulated client-side
- Allow downgrade to a less secure authorization method
- Skip authorization for transactions matching attack patterns (adding/removing parameters)
- Allow transaction data to be modified after authorization begins without restarting the flow
- Accept the same authorization credentials across multiple transactions (replay risk)
- Build new authorization flows on top of old insecure codebases

## ALWAYS
- Enforce all authorization logic server-side with default-deny
- Apply What You See Is What You Sign (WYSIWYS): display critical transaction data (target account, amount, type) before the user authorizes
- Separate the authentication process from the transaction authorization process
- Require re-authorization via the current method for any change to authorization tokens or methods
- Generate unique, time-limited credentials per transaction (timestamp, sequence number, or random value)
- Enforce sequential state transitions — prevent step skipping and out-of-order execution
- Invalidate authorization data immediately if transaction data is modified; reset the flow
- Encrypt all client-server transaction data for confidentiality and integrity; verify server-side
- Implement brute-force protection: restart full transaction flow after failed attempts; apply throttling
- Generate and store all significant transaction data server-side; pass to authorization component without client touch
- Log and monitor authorization modification attempts
- Use secure elements (TEE, TPM, smart cards) for signing key storage; protect with second factor

## Transaction State Flow

```
1. User enters transaction data
2. User requests authorization
3. App initializes authorization mechanism (server-side)
4. User verifies/confirms displayed transaction data (WYSIWYS)
5. User submits authorization credentials
6. App validates credentials server-side → executes transaction
```

## Checklist
- [ ] Authorization logic is entirely server-side; no client influence on result
- [ ] Authentication and transaction authorization use distinct methods/credentials
- [ ] WYSIWYS: critical transaction data shown to user before credential submission
- [ ] Authorization credentials are unique per transaction and time-limited
- [ ] Transaction data modification resets the entire authorization flow
- [ ] Sequential state transitions enforced; skipping steps is impossible
- [ ] Brute-force protection: throttling and full restart after failures
- [ ] Authorization method downgrade to weaker method is blocked
