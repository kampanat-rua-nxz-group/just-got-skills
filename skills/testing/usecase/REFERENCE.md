# Use Case Map — Reference

Consult for outline examples, rendering errors, or XMind compatibility.

## Default routing errors

Use these default contracts for method and path validation unless the user or supplied API contract explicitly overrides them. These routing errors contain only `error.code` and `error.message`; they have no `type` or `field` key.

| Case | HTTP status | Exact response body |
| --- | --- | --- |
| Method not allowed | 405 | `{"error":{"code":"invalid_method","message":"Method not allowed"}}` |
| Path not found | 404 | `{"error":{"code":"invalid_path","message":"Path not found"}}` |

Capture the status, code and message as leaves beneath each sample input, as in the example below. Cite this default under Open Questions / Notes when a feature document does not repeat it; the two cases are defined defaults, not `TBD` forks.

## Full Annotated Example

The contracts below are illustrative. This example’s `GET /ethereum/transfers` accepts an optional integer `limit` from 1 to 100 (default 20) and an optional `status` enum (`pending`, `confirmed`). Invalid query values return HTTP 400 with code `invalid_query`. Use the supplied feature contract in real maps.

```markdown
# Chain Connector API

## Validation Cases
- POST /ethereum/build-transfer
  - Method
    - invalid method
      - Sample input: DELETE /ethereum/build-transfer
        - HTTP Status 405
        - error code invalid_method
        - message "Method not allowed"
        - error contains only code and message (no type or field)
  - Path/Endpoint
    - invalid path
      - Sample input: POST /ethereum/build-transfer-unknown
        - HTTP Status 404
        - error code invalid_path
        - message "Path not found"
        - error contains only code and message (no type or field)
  - Headers
    - content-type
      - Omit field
        - Sample input: Content-Type header omitted; otherwise valid JSON body
          - HTTP Status 400
          - error code LB_API_ERC_001
      - Content-Type mismatch @TBD
        - Sample input: Content-Type=text/plain or application/xml; otherwise valid JSON body
          - HTTP Status TBD
          - error code TBD
    - x-service-name
      - Omit field
        - Sample input: x-service-name header omitted; all other headers valid
          - HTTP Status 400
          - error code LB_API_ERC_001
  - Request body
    - from_address
      - **Omit required field**
        - Sample input: remove from_address from an otherwise valid body
          - HTTP Status 400
          - error code LB_API_ERC_001
      - **Address without 0x prefix**
        - Sample input: from_address="1111111111111111111111111111111111111111" or "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
          - HTTP Status 400
          - error code LB_API_ERC_002

- GET /ethereum/transfers
  - Query parameters
    - limit
      - Omit optional parameter
        - Sample input: GET /ethereum/transfers (no query string)
          - HTTP Status 200
          - default page limit is 20
      - Empty or whitespace
        - Sample input: ?limit= or ?limit=%20 or ?limit=%20%20
          - HTTP Status 400
          - error code invalid_query
      - Wrong type or malformed integer
        - Sample input: ?limit=abc or ?limit=1.5 or ?limit=true or ?limit=null
          - HTTP Status 400
          - error code invalid_query
      - Below minimum
        - Sample input: ?limit=0 or ?limit=-1
          - HTTP Status 400
          - error code invalid_query
      - Within inclusive boundaries
        - Sample input: ?limit=1 or ?limit=2 or ?limit=99 or ?limit=100
          - HTTP Status 200
          - returned item count does not exceed the requested limit
      - Above maximum
        - Sample input: ?limit=101 or ?limit=1000
          - HTTP Status 400
          - error code invalid_query
    - status
      - Omit optional parameter
        - Sample input: ?limit=20 (status omitted)
          - HTTP Status 200
          - results may contain both pending and confirmed transfers
      - Supported enum value
        - Sample input: ?status=pending or ?status=confirmed
          - HTTP Status 200
          - each returned transfer matches the requested status
      - Empty or whitespace
        - Sample input: ?status= or ?status=%20
          - HTTP Status 400
          - error code invalid_query
      - Unsupported value or wrong type
        - Sample input: ?status=failed or ?status=123 or ?status=null
          - HTTP Status 400
          - error code invalid_query
      - Case sensitivity undefined @TBD
        - Sample input: ?status=PENDING or ?status=Confirmed
          - HTTP Status TBD
          - response behavior TBD

## Business Scenarios
- POST /ethereum/build-transfer
  - Service unavailable @edge
    - Sample data test: service health check fails
      - HTTP Status 503
      - error code LB_API_SVC_001
  - Service available
    - Ethereum RPC down / timeout @edge @mock-only
      - Sample data test: RPC request times out through toxiproxy
        - HTTP Status 500
        - error code LB_API_ETH_004
    - RPC available
      - Authentication failure @security
        - Sample data test: missing authentication credentials
          - HTTP Status 401
          - error code LB_API_AUTH_001
      - Authenticated
        - amount < minimum required
          - Sample data test: amount below documented minimum
            - HTTP Status 400
            - error code LB_API_AMT_001
            - message "amount below minimum"
        - amount > maximum required
          - Sample data test: amount above documented maximum
            - HTTP Status 400
            - error code LB_API_AMT_002
        - Amount within allowed range
          - **Insufficient balance**
            - Sample data test: balance below requested amount
              - HTTP Status 422
              - error code LB_API_BAL_001
          - Balance sufficient
            - Sample data test: sufficient balance for transfer
              - HTTP Status 200
              - calldata decodes to requested transfer args

## Cross-cutting (Security & Edge)
- Security
  - **SQL/command injection in address field** @security
  - Oversized payload @security
- Edge Cases
  - **Concurrent broadcast race**
    - Sample data test: submit two simultaneous identical broadcasts
      - exactly one on-chain transaction

## Open Questions / Notes
- POST /ethereum/build-transfer
  - Source: [[2026-06-12-post-ethereum-build-transfer]]
  - Method and Path/Endpoint: routing contracts use the skill’s default routing errors
  - Content-Type mismatch: should text/plain and application/xml return 415 or be parsed anyway?
  - Business Scenarios: assumes schema-valid input covered by Validation Cases
  - Skipped gate: authorization — no per-service roles on this endpoint
  - Ethereum RPC down / timeout
    - Prep: toxiproxy between service and node for fault injection
  - Success
    - Steps: POST valid body, decode calldata, assert arguments match request
- GET /ethereum/transfers
  - status case sensitivity: are PENDING and Confirmed accepted or rejected?
  - Scope: query-validation excerpt; business decision tree still needs mapping
- Concurrent broadcast race
  - Prep: submit two simultaneous identical broadcasts

## Coverage Gaps
- @TBD forks
  - Content-Type mismatch on POST /ethereum/build-transfer — HTTP status and error code undefined
  - status case sensitivity on GET /ethereum/transfers — response behavior undefined
- Unmapped flow: business decision tree for GET /ethereum/transfers
- Skipped gates: authorization on POST /ethereum/build-transfer — no roles
- Gates with continuation but no fail fork: (none)
```

## Notes

- The script reports malformed input by line number. Correct the outline and render again.
- Output uses the XMind 2020+ JSON archive format (`content.json`, `metadata.json`, and `manifest.json`). XMind 26.x opens it with full note support; XMind 8 is unsupported.
- Bullets at the same indentation are siblings anchored to the nearest heading. Regression-test this after script changes; a previous bug nested siblings as children.
