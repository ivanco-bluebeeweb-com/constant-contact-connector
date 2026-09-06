# Constant Contact Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **Constant Contact** under category **C30. Email Marketing & Newsletter**. The integration interfaces directly with the official **Constant Contact REST API v3** (`https://api.cc.email/v3`), providing complete visibility and management of contacts, email campaigns, contact lists, segments, automations, email templates, and audience delivery health audits.

## Official API Specifications
- **API Architecture:** RESTful JSON API v3
- **Base URL:** `https://api.cc.email/v3`
- **Core Endpoints:**
  - `GET /account/summary` — verify token privileges and account context
  - `GET /contacts` — list contacts with cursor pagination and status filters
  - `GET /contacts/{contact_id}` — detailed contact record with list memberships
  - `POST /contacts` — create or upsert contact record
  - `DELETE /contacts/{contact_id}` — delete contact
  - `GET /emails` — list email marketing campaigns
  - `GET /emails/{campaign_id}` — detailed campaign status and delivery metrics
  - `GET /contact_lists` — static audience mailing lists
  - `GET /segments` — dynamic condition-based audience segments
  - `GET /templates` — reusable email layout HTML templates
- **Authentication Model:** Bearer Token via `Authorization: Bearer <api_key>` (OAuth2 Access Token)
- **Mandatory Requirements:**
  - Strict error classification: HTTP 429 rate limits with Retry-After extraction, HTTP 401/403 differentiation (Standard B8/B10).
  - Sanitization of Bearer tokens in error traces and diagnostic payloads (Standard B8).
  - Multi-tenant connection tracking and isolation via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with Constant Contact REST API v3 specifications.
2. [x] Core resource endpoints and Bearer auth verified against official docs.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with B8-B10 compliance, secret redaction, and error mapping.
5. [ ] Authenticated live testing on an authorized account before publishing.
