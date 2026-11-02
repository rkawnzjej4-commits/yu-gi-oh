"""Audit recorded card approvals; does not establish official evidence or deck legality."""

import argparse
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

CUTOFF = date(2012, 3, 31)


def is_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def is_hash(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def is_url(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
    except ValueError:
        return False


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def object_field(record, name):
    value = record.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def snapshot_issues(snapshot):
    if snapshot is None:
        return ["snapshot: unverified"]
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object or null")
    checks = {
        "id": nonempty,
        "rules_verified_at": is_date,
        "rules_source_url": is_url,
        "engine_sha256": is_hash,
        "scripts_sha256": is_hash,
        "card_data_sha256": is_hash,
    }
    return [f"snapshot: invalid {key}" for key, check in checks.items()
            if not check(snapshot.get(key))]


def card_issues(card, snapshot):
    issues = []
    eligibility = object_field(card, "eligibility")
    text = object_field(card, "text")
    impl = object_field(card, "implementation")
    if eligibility.get("status") != "verified":
        issues.append("eligibility: not verified")
    if eligibility.get("territory") != "JP-OCG":
        issues.append("eligibility: not JP-OCG")
    released = eligibility.get("first_release_date")
    if not is_date(released):
        issues.append("eligibility: missing or invalid first release date")
    elif date.fromisoformat(released) > CUTOFF:
        issues.append("eligibility: after cutoff")
    for field, check in (("evidence_url", is_url), ("verified_at", is_date)):
        if not check(eligibility.get(field)):
            issues.append(f"eligibility: invalid {field}")
    if text.get("status") != "verified":
        issues.append("text: not verified")
    for field, check in (("source_url", is_url), ("verified_at", is_date), ("sha256", is_hash)):
        if not check(text.get(field)):
            issues.append(f"text: invalid {field}")
    if impl.get("status") != "verified":
        issues.append("implementation: not verified")
    if not snapshot or impl.get("snapshot_id") != snapshot.get("id"):
        issues.append("implementation: snapshot mismatch")
    if not is_hash(impl.get("text_sha256")) or impl.get("text_sha256") != text.get("sha256"):
        issues.append("implementation: text hash mismatch")
    tests = impl.get("tests")
    if not isinstance(tests, list) or not tests:
        issues.append("implementation: no test results")
    else:
        ids = set()
        for test in tests:
            if not isinstance(test, dict) or not nonempty(test.get("id")):
                issues.append("implementation: invalid test result")
                continue
            if test["id"] in ids:
                issues.append("implementation: duplicate test id")
            ids.add(test["id"])
            if test.get("result") != "passed":
                issues.append("implementation: test did not pass")
    return issues


def audit(catalog):
    if not isinstance(catalog, dict):
        raise ValueError("catalog must be an object")
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    if catalog.get("cutoff") != CUTOFF.isoformat():
        raise ValueError("cutoff must be 2012-03-31")
    cards = catalog.get("cards")
    if not isinstance(cards, list):
        raise ValueError("cards must be a list")
    snapshot = catalog.get("snapshot")
    global_issues = snapshot_issues(snapshot)
    ids = set()
    results = []
    for card in cards:
        if not isinstance(card, dict) or not nonempty(card.get("card_id")):
            raise ValueError("every card needs a nonempty card_id")
        if card["card_id"] in ids:
            raise ValueError(f"duplicate card_id: {card['card_id']}")
        ids.add(card["card_id"])
        if not nonempty(card.get("name_ja")):
            raise ValueError("every card needs name_ja")
        issues = global_issues + card_issues(card, snapshot)
        results.append({"card_id": card["card_id"], "supported": not issues, "issues": issues})
    return {"snapshot_issues": global_issues, "cards": results,
            "supported_count": sum(item["supported"] for item in results)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.catalog.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["cards"]:
        return 2
    return 0 if result["supported_count"] == len(result["cards"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
