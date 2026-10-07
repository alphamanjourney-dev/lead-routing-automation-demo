#!/usr/bin/env python3
"""Zero-dependency lead intake / qualification / routing demo.

Designed as a portfolio proof asset for business-automation work:
- validates inbound lead data
- normalizes identity fields
- deduplicates repeat leads
- scores commercial intent
- routes deterministically by geography and score
- emits structured results and operational stats

No external services or secrets are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HIGH_INTENT_TERMS = {
    "automation",
    "ai agent",
    "crm",
    "lead routing",
    "workflow",
    "whatsapp",
    "integration",
    "api",
    "webhook",
}
LATAM = {"BR", "MX", "AR", "CL", "CO", "PE", "UY", "PY", "EC"}
NORTH_AMERICA = {"US", "CA"}

TEAM_POOLS = {
    "north-america": ["na-ae-1", "na-ae-2"],
    "latam": ["latam-ae-1", "latam-ae-2"],
    "global": ["global-ae-1", "global-ae-2"],
}


@dataclass(frozen=True)
class Decision:
    fingerprint: str
    score: int
    priority: str
    region: str
    owner: str
    normalized: dict[str, Any]


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    out = dict(raw)
    out["name"] = str(raw.get("name", "")).strip()
    out["email"] = str(raw.get("email", "")).strip().lower()
    out["phone"] = _digits(str(raw.get("phone", "")))
    out["country"] = str(raw.get("country", "")).strip().upper()
    out["service_interest"] = str(raw.get("service_interest", "")).strip().lower()
    out["message"] = str(raw.get("message", "")).strip().lower()
    out["source"] = str(raw.get("source", "")).strip().lower()
    try:
        out["budget"] = float(raw.get("budget") or 0)
    except (TypeError, ValueError):
        out["budget"] = 0.0
    try:
        out["company_size"] = int(raw.get("company_size") or 0)
    except (TypeError, ValueError):
        out["company_size"] = 0
    return out


def validate(lead: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not lead["name"]:
        errors.append("missing_name")
    if not lead["email"] and not lead["phone"]:
        errors.append("missing_contact")
    if lead["email"] and not EMAIL_RE.match(lead["email"]):
        errors.append("invalid_email")
    if lead["phone"] and len(lead["phone"]) < 8:
        errors.append("invalid_phone")
    return errors


def fingerprint(lead: dict[str, Any]) -> str:
    identity = lead["email"] or lead["phone"] or lead["name"].lower()
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def score(lead: dict[str, Any]) -> int:
    value = 10
    if lead["budget"] >= 10000:
        value += 35
    elif lead["budget"] >= 5000:
        value += 25
    elif lead["budget"] >= 1000:
        value += 15

    if lead["company_size"] >= 50:
        value += 20
    elif lead["company_size"] >= 10:
        value += 12
    elif lead["company_size"] >= 2:
        value += 5

    haystack = f"{lead['service_interest']} {lead['message']}"
    matched = sum(1 for term in HIGH_INTENT_TERMS if term in haystack)
    value += min(matched * 5, 20)

    if lead["source"] in {"referral", "partner", "existing-client"}:
        value += 10
    elif lead["source"] in {"website", "inbound", "demo"}:
        value += 5

    return min(value, 100)


def region_for(country: str) -> str:
    if country in NORTH_AMERICA:
        return "north-america"
    if country in LATAM:
        return "latam"
    return "global"


def owner_for(fp: str, region: str) -> str:
    pool = TEAM_POOLS[region]
    idx = int(fp[:8], 16) % len(pool)
    return pool[idx]


def priority_for(score_value: int) -> str:
    if score_value >= 70:
        return "hot"
    if score_value >= 40:
        return "qualified"
    return "nurture"


def decide(raw: dict[str, Any]) -> Decision:
    lead = normalize(raw)
    errors = validate(lead)
    if errors:
        raise ValueError(",".join(errors))
    fp = fingerprint(lead)
    value = score(lead)
    region = region_for(lead["country"])
    return Decision(
        fingerprint=fp,
        score=value,
        priority=priority_for(value),
        region=region,
        owner=owner_for(fp, region),
        normalized=lead,
    )


def process(leads: Iterable[dict[str, Any]]) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    seen: set[str] = set()

    for index, raw in enumerate(leads, start=1):
        lead = normalize(raw)
        try:
            errors = validate(lead)
            if errors:
                raise ValueError(",".join(errors))
            fp = fingerprint(lead)
            if fp in seen:
                duplicates.append({"row": index, "fingerprint": fp, "lead": lead})
                continue
            seen.add(fp)
            decision = decide(lead)
            accepted.append(
                {
                    "row": index,
                    "fingerprint": decision.fingerprint,
                    "score": decision.score,
                    "priority": decision.priority,
                    "region": decision.region,
                    "owner": decision.owner,
                    "lead": decision.normalized,
                }
            )
        except Exception as exc:
            invalid.append({"row": index, "error": str(exc), "lead": lead})

    stats = {
        "input": len(accepted) + len(duplicates) + len(invalid),
        "accepted": len(accepted),
        "duplicates": len(duplicates),
        "invalid": len(invalid),
        "hot": sum(1 for x in accepted if x["priority"] == "hot"),
        "qualified": sum(1 for x in accepted if x["priority"] == "qualified"),
        "nurture": sum(1 for x in accepted if x["priority"] == "nurture"),
    }
    return {"accepted": accepted, "duplicates": duplicates, "invalid": invalid, "stats": stats}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                rows.append({"name": "", "_parse_error": f"line {line_number}: {exc}"})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = process(read_jsonl(args.input))
    encoded = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
