# Lead Routing Automation Demo

A zero-dependency portfolio proof asset for AI/business-automation work.

## Business problem

A company receives leads from forms, email, webhooks, WhatsApp, spreadsheets, or other channels. Manual intake creates duplicate records, bad data, slow follow-up, and dropped leads.

This demo implements the core automation logic locally:

1. normalize incoming lead data;
2. validate contact data;
3. deduplicate repeat leads;
4. score commercial intent;
5. classify priority;
6. assign region;
7. deterministically route to an owner;
8. separate invalid records for recovery;
9. produce operational stats.

The design intentionally uses deterministic code rather than an external LLM so the critical routing logic is testable, cheap, and reliable. An LLM classification/enrichment node can be inserted as an optional upstream step in a real n8n/Make/custom implementation.

## Run

```bash
python3 lead_router.py sample-leads.jsonl --output result.json
python3 -m unittest -v
```

## What this proves

- API/webhook-style data transformation
- validation and structured failure paths
- idempotency/deduplication thinking
- lead scoring and routing logic
- deterministic assignment
- explicit QA/tests
- clear separation of business logic from integrations

## Production extension

A real deployment would connect adapters around the core:

`Form / WhatsApp / Email / Webhook -> Normalize -> Optional AI classify/enrich -> Validate -> Dedupe -> Score -> Route -> CRM -> Slack/Email/WhatsApp notification -> Retry/dead-letter/logging`

Typical integrations:
- n8n / Make / Zapier
- HubSpot / Pipedrive / GoHighLevel / Airtable
- Twilio / WhatsApp
- Slack / Gmail
- OpenAI / Claude for optional classification/extraction
- PostgreSQL / Redis / platform datastore for persistent idempotency

## Privacy

Sample data is fictional. No owner/client private data or secrets are included.
