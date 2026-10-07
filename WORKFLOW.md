# Workflow Mapping

## Intake
Accept JSON payload from a form, webhook, email parser, WhatsApp adapter, or spreadsheet row.

## Normalize
Canonicalize email, phone, country, source, budget, company size, service interest, and message.

## Validate
Reject missing contact methods, malformed emails, and clearly invalid phones into a recoverable invalid queue.

## Deduplicate
Create a stable fingerprint from normalized email/phone. In production, persist the idempotency key before CRM writes.

## Score
Combine explicit budget/company-size signals with service-intent keywords and source quality.

## Route
Map geography to a regional pool, then assign deterministically. Higher-scoring leads can trigger faster SLA paths.

## CRM + Notifications
Create/update the CRM record only after validation/deduplication. Notify the assigned owner and log the decision.

## Failure handling
Use retry-with-backoff for transient API errors. Send permanent failures to a dead-letter/review queue with enough context to replay safely.
