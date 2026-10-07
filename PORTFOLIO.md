# Portfolio Proof — Lead Qualification & Routing Automation

**Professional identity:** Povils Brandt  
**Service focus:** AI/business automation, API and webhook integrations, CRM workflows, lead handling, reliable multi-step systems.

## Problem

Businesses often receive leads from many channels but still rely on manual copy/paste, inconsistent qualification, duplicate CRM records, and slow follow-up.

## What this demo implements

A deterministic core that:
- validates and normalizes inbound lead records;
- deduplicates repeat contacts;
- scores commercial intent;
- classifies hot / qualified / nurture leads;
- routes by geography and deterministic ownership;
- separates invalid records for replay/recovery;
- emits operational metrics;
- includes automated tests.

## Why deterministic core logic matters

LLMs are useful for extracting/classifying unstructured information, but critical routing and CRM-write rules should remain testable and predictable. A production version can use an AI model upstream for enrichment while retaining deterministic validation, idempotency, routing, and recovery logic.

## Real-world architecture

`Website / WhatsApp / Email / Form / Webhook -> normalize -> optional AI extract/classify -> validate -> dedupe -> score -> route -> CRM -> notifications -> logs/retries/dead-letter`

## Relevant delivery capabilities

- REST APIs and webhooks
- CRM integration and deduplication
- WhatsApp/messaging workflow integration
- AI/LLM classification steps
- retries, idempotency and failure recovery
- structured testing and documentation
- custom code when no-code automation is insufficient

## Verification

Run:

```bash
python3 -m unittest -v
python3 lead_router.py sample-leads.jsonl --output result.json
```

Current verification: **5/5 tests pass**.

## Privacy

All sample data is fictional. No private client or owner data is included.
