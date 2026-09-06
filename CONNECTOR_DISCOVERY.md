# Constant Contact Connector — API Discovery

## Provider Overview
- **Vendor:** Constant Contact, Inc.
- **Service:** Small-business email marketing, SMS, contact management, and automation.
- **Official Documentation:** `https://developer.constantcontact.com/api_reference/index.html`

## API Protocols and Endpoints
- **Base URL:** `https://api.cc.email/v3`
- **Supported Authentication:** OAuth 2.0 Bearer Token (`contact_data`, `campaign_data`).
- **Rate Limits:** Constant Contact enforces tiered requests per second/minute quotas; HTTP 429 returns standard retry headers.
- **Pagination:** Cursor-based via next links in JSON responses.
