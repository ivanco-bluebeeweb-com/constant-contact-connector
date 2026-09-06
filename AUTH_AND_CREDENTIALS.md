# Constant Contact Connector — Authentication and Credentials

## Auth Architecture
- **Standard:** `AUTH_AND_CREDENTIALS_STANDARD.md` (B1–B10)
- **Primary Auth Mode:** OAuth 2.0 Bearer Access Token / API Key.
- **Header:** `Authorization: Bearer <api_key>`
- **Token Redaction:** All diagnostic traces and error wrappers execute `_sanitize_msg` to mask raw credentials.
- **Connection Isolation:** Handlers accept explicit `connection_id` and isolate multi-tenant credentials per Imperal user.
