# Use Case Map — Reference

Detailed examples and operational notes. Not loaded by default — consult when the compact SKILL.md leaves a format question open.

## Full Annotated Example

```markdown
# Chain Connector API

## Validation Cases
- POST /ethereum/build-transfer
  > Spec: [[2026-06-12-post-ethereum-build-transfer]]
  - Method
    - invalid method
      - HTTP Status 405
  - Path/Endpoint
    - invalid path
      - HTTP Status 404
  - Headers
    - content-type
      - Omit field
        - HTTP Status 400
        - error code LB_API_ERC_001
      - Content-Type mismatch (text/plain or missing) @blocked-tbd
        > Define: 415 or parsed anyway
        - HTTP Status TBD
        - error code TBD
    - x-service-name
      - Omit field
        - HTTP Status 400
        - error code LB_API_ERC_001
  - Request body
    - from_address
      - Omit required field [!]
        - HTTP Status 400
        - error code LB_API_ERC_001
      - Address without 0x prefix [!]
        - HTTP Status 400
        - error code LB_API_ERC_002

## Business Scenarios
- POST /ethereum/build-transfer
  > assumes: request schema-valid (see [[Validation Cases]])
  - Service unavailable @edge
    - HTTP Status 503
    - error code LB_API_SVC_001
  - Service available
    - Ethereum RPC down / timeout @edge @mock-only
      > Prep: toxiproxy between service and node — cannot force real outage
      - HTTP Status 500
      - error code LB_API_ETH_004
    - RPC available
      - Authentication failure @security
        - HTTP Status 401
        - error code LB_API_AUTH_001
      - Authentication success
        > skip: authorization — no per-service roles on this endpoint
        - amount < minimum required
          - HTTP Status 400
          - error code LB_API_AMT_001
          - message "amount below minimum"
        - amount > maximum required
          - HTTP Status 400
          - error code LB_API_AMT_002
        - minimum <= amount <= maximum
          - Insufficient balance
            - HTTP Status 422
            - error code LB_API_BAL_001
          - Sufficient balance
            - → Success [!]
              > Steps: POST valid body → decode calldata, assert args match request
              - HTTP Status 200
              - calldata decodes to requested transfer args

## Cross-cutting (Security & Edge)
- Security
  - SQL/command injection in address field [!] @security
  - Oversized payload @security
- Edge Cases
  - Concurrent broadcast race [!]
    > Two simultaneous identical broadcasts — exactly one on-chain tx

## Coverage Gaps
- Blocked / TBD forks: Content-Type mismatch on POST /ethereum/build-transfer — HTTP status and error code undefined
- Skipped gates: authorization on POST /ethereum/build-transfer — no roles
- Gates with continuation but no fail fork: (none)
```

## Notes

- Script validates the outline and fails with a line number on malformed input — fix the outline, don't patch the script output.
- Output uses XMind 2020+ JSON archive format (`content.json`, `metadata.json`, and `manifest.json`). Opens natively in XMind 26.x with full note support. Not backward-compatible with XMind 8.
- Same-indent bullets are siblings (anchored to the nearest heading) — regression-test this after any script change; a past bug chained them as children.
