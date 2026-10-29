"""Independent source-inventory completeness checks for Mandros Blind.

The validator compares a source-derived expected-finding inventory with the
normalized extraction.  It never creates values and never treats a matching
outcome name alone as proof of completeness.
"""

from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
    "VERIFIED",
    "MISSING_FROM_EXTRACTION",
    "PRESENT_BUT_INCOMPLETE",
    "STATISTICAL_TYPE_MISMATCH",
    "NUMERICAL_MISMATCH",
    "SOURCE_CONFLICT",
    "NOT_REPORTED_IN_SOURCE",
    "REQUIRES_MANUAL_REVIEW",
}


def validate_source_inventory(bundle: dict[str, Any]) -> dict[str, Any]:
    inventory = list(bundle.get("source_inventory") or [])
    extracted_ids = {
        str(row.get("id"))
        for group in (bundle.get("baseline") or [], bundle.get("outcomes") or [])
        for row in group
        if row.get("id")
    }
    extracted_ids.update(
        str(row.get("test_id"))
        for row in bundle.get("statistical_tests") or []
        if row.get("test_id")
    )

    checked: list[dict[str, Any]] = []
    for item in inventory:
        row = dict(item)
        status = str(row.get("status") or "REQUIRES_MANUAL_REVIEW")
        linked = [str(value) for value in row.get("extraction_ids") or [] if value]
        missing_links = [value for value in linked if value not in extracted_ids]
        if status not in ALLOWED_STATUSES:
            status = "REQUIRES_MANUAL_REVIEW"
        if status == "VERIFIED" and missing_links:
            status = "MISSING_FROM_EXTRACTION"
        row["status"] = status
        row["missing_extraction_ids"] = missing_links
        checked.append(row)

    counts = Counter(row["status"] for row in checked)
    unresolved = sum(value for key, value in counts.items() if key != "VERIFIED" and key != "NOT_REPORTED_IN_SOURCE")
    independently_inventoried = bool(bundle.get("source_inventory_independent"))
    all_verified = bool(checked) and independently_inventoried and unresolved == 0
    return {
        "validator": "source_based_numerical_completeness_v1",
        "inventory_independent_of_excel": independently_inventoried,
        "inventory_scope": bundle.get("source_inventory_scope") or "not_declared",
        "expected_finding_count": len(checked),
        "status_counts": dict(sorted(counts.items())),
        "unresolved_count": unresolved,
        "complete_and_verified": all_verified,
        "claim": "100% verified" if all_verified else "not demonstrated",
        "findings": checked,
        "safeguard": "Missing or unavailable source values remain blank; the validator never generates numbers.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a source-completeness report for a versioned Mandros Blind dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.dataset.read_text(encoding="utf-8"))
    report = validate_source_inventory(bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)
    print(json.dumps({key: report[key] for key in ("expected_finding_count", "status_counts", "unresolved_count", "claim")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

