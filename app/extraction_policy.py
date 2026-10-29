"""Automatic Phase 1 extraction-skill loading and dataset safeguards.

This module is deliberately additive.  It does not extract or replace a
scientific value.  It makes the versioned prompt/skill mandatory at runtime,
records their hashes, and detects representation failures before export.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROMPT_RELATIVE = Path("standards/optimal_extraction_prompt_v1.md")
STATISTICS_RELATIVE = Path("standards/clinical_trial_statistics_v1.json")
PHASE1_RELATIVE = Path("standards/phase1_policy_v1.json")
CONTRACT_RELATIVE = Path("standards/system_contract_v1.json")
SKILL_RELATIVE = Path("skills/mandoros-blind-phase1-statistical-integrity/SKILL.md")


class ExtractionPolicyError(RuntimeError):
    """Raised when the mandatory extraction skill bundle is unavailable."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_policy_bundle(root: Path) -> dict[str, Any]:
    paths = {
        "prompt": root / PROMPT_RELATIVE,
        "statistics": root / STATISTICS_RELATIVE,
        "phase1_policy": root / PHASE1_RELATIVE,
        "system_contract": root / CONTRACT_RELATIVE,
        "skill": root / SKILL_RELATIVE,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ExtractionPolicyError("Mandatory extraction-skill files are missing: " + ", ".join(missing))

    prompt = paths["prompt"].read_text(encoding="utf-8")
    required_prompt_sections = (
        "## Role and fixed boundary",
        "## Required workflow",
        "## Atomic extraction rules",
        "## Statistical meaning",
        "## Completeness and provenance statuses",
        "## Acceptance gate",
    )
    absent = [heading for heading in required_prompt_sections if heading not in prompt]
    if absent:
        raise ExtractionPolicyError("Extraction prompt is incomplete; missing sections: " + ", ".join(absent))
    statistics = json.loads(paths["statistics"].read_text(encoding="utf-8"))
    phase1 = json.loads(paths["phase1_policy"].read_text(encoding="utf-8"))
    contract = json.loads(paths["system_contract"].read_text(encoding="utf-8"))
    skill_text = paths["skill"].read_text(encoding="utf-8")
    if "name: mandoros-blind-phase1-statistical-integrity" not in skill_text:
        raise ExtractionPolicyError("The required Phase 1 skill has invalid frontmatter.")
    return {
        "policy_id": "mandros-blind-optimal-rct-extraction-v1",
        "automatic_application": True,
        "prompt_version": "1.1.0",
        "statistics_version": statistics.get("version"),
        "phase1_policy_version": phase1.get("version"),
        "system_contract_version": contract.get("version"),
        "files": {
            key: {"path": str(path.relative_to(root)), "sha256": _sha256(path)}
            for key, path in paths.items()
        },
    }


def evaluate_dataset(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Return representation violations without changing scientific content."""
    issues: list[dict[str, Any]] = []
    outcomes = list(dataset.get("outcomes") or [])
    baseline = list(dataset.get("baseline") or [])
    tests = list(dataset.get("statistical_tests") or [])
    arm_rows = list(dataset.get("arms") or [])
    arms = {str(row.get("arm_id")) for row in arm_rows if row.get("arm_id")}
    arm_randomized_n = {
        str(row.get("arm_id")): row.get("n_randomized")
        for row in arm_rows if row.get("arm_id")
    }
    strict_source_tuple_validation = bool(dataset.get("strict_source_tuple_validation"))
    source_inventory = list(dataset.get("source_inventory") or [])
    allowed_inventory_statuses = {
        "VERIFIED", "MISSING_FROM_EXTRACTION", "PRESENT_BUT_INCOMPLETE",
        "STATISTICAL_TYPE_MISMATCH", "NUMERICAL_MISMATCH", "SOURCE_CONFLICT",
        "NOT_REPORTED_IN_SOURCE", "REQUIRES_MANUAL_REVIEW",
    }

    if not dataset.get("source_inventory_independent") or not source_inventory:
        issues.append({
            "code": "POLICY_NO_INDEPENDENT_SOURCE_INVENTORY", "severity": "critical", "blocking": True,
            "message": "Scientific completeness cannot be validated without a PDF-first inventory independent of the Excel output.",
        })
    invalid_statuses = sorted({str(row.get("status")) for row in source_inventory if row.get("status") not in allowed_inventory_statuses})
    if invalid_statuses:
        issues.append({
            "code": "POLICY_INVALID_INVENTORY_STATUS", "severity": "critical", "blocking": True,
            "message": "Source inventory contains unsupported statuses: " + ", ".join(invalid_statuses),
        })

    if dataset.get("generation_mode") == "generic_pdf_mandros":
        issues.append({
            "code": "POLICY_GENERIC_DRAFT_ONLY", "severity": "critical", "blocking": True,
            "message": "The generic adapter normalized Mandros rows but did not independently extract and reconcile the full PDF; export is draft-only.",
        })

    primary = dataset.get("primary_endpoint") or {}
    if strict_source_tuple_validation:
        required_ids = set(primary.get("required_record_ids") or [])
        available_ids = {str(row.get("id")) for row in outcomes if row.get("id")}
        missing_primary_ids = sorted(required_ids - available_ids)
        if not primary or missing_primary_ids:
            issues.append({
                "code": "POLICY_PRIMARY_ENDPOINT_GATE_FAILED", "severity": "critical", "blocking": True,
                "message": "Primary-endpoint tuple is absent or incomplete" + (f"; missing records: {', '.join(missing_primary_ids)}" if missing_primary_ids else "."),
            })

        tuple_keys: dict[tuple[Any, ...], str] = {}
        for row in [*baseline, *outcomes]:
            key = (
                row.get("independent_study_id"), row.get("domain") or "baseline",
                row.get("outcome") or row.get("characteristic"), row.get("arm_id"),
                row.get("comparison_id"), row.get("timepoint"), row.get("time_unit"),
                row.get("analysis_population"), row.get("measure"), row.get("unit"),
                row.get("subgroup_type"), row.get("subgroup_value"),
                row.get("threshold_lt"), row.get("threshold_eq"), row.get("threshold_gt"),
                row.get("threshold_value"), row.get("threshold_unit"),
            )
            if key in tuple_keys:
                issues.append({
                    "code": "POLICY_DUPLICATE_SOURCE_IDENTITY_TUPLE", "severity": "critical", "blocking": True,
                    "record_id": row.get("id"),
                    "message": f"Record duplicates the full source identity tuple of {tuple_keys[key]}.",
                })
            else:
                tuple_keys[key] = str(row.get("id"))
            if row.get("source_status") == "published_main_article_exact" and not row.get("source_location"):
                issues.append({
                    "code": "POLICY_EXACT_WITHOUT_SOURCE_LOCATION", "severity": "major", "blocking": False,
                    "record_id": row.get("id"), "message": "Exact-source record has no table/figure/text locator.",
                })

    identifiers = [str(row.get("id")) for row in [*baseline, *outcomes] if row.get("id")]
    if len(identifiers) != len(set(identifiers)):
        issues.append({
            "code": "POLICY_DUPLICATE_RECORD_ID", "severity": "critical", "blocking": True,
            "message": "Baseline/outcome record identifiers are not unique.",
        })

    for row in [*baseline, *outcomes]:
        record_id = row.get("id")
        arm_id = row.get("arm_id")
        if arm_id and str(arm_id) not in arms:
            issues.append({
                "code": "POLICY_INVALID_ARM_REFERENCE", "severity": "critical", "blocking": True,
                "record_id": record_id, "message": f"Record references unknown arm_id {arm_id!r}.",
            })
        lower, upper = row.get("lower_value"), row.get("upper_value")
        ci_lower, ci_upper = row.get("ci_lower"), row.get("ci_upper")
        estimate_type = str(row.get("estimate_type") or row.get("measure") or "").lower()
        if "median" in estimate_type and lower is not None and upper is not None and lower == ci_lower and upper == ci_upper:
            issues.append({
                "code": "POLICY_IQR_DUPLICATED_AS_CI", "severity": "critical", "blocking": True,
                "record_id": record_id, "message": "IQR bounds are duplicated in confidence-interval fields.",
            })
        if row.get("event_count") is not None and str(row.get("event_count_unit") or "").strip() == "%":
            issues.append({
                "code": "POLICY_EVENT_COUNT_PERCENT_UNIT", "severity": "critical", "blocking": True,
                "record_id": record_id, "message": "An event count uses percent as its count unit.",
            })
        if (
            str(row.get("domain") or "").lower() == "safety"
            and str(row.get("subgroup_type") or "").lower() == "sex"
            and row.get("denominator") is not None
            and row.get("denominator") == arm_randomized_n.get(str(arm_id))
        ):
            issues.append({
                "code": "POLICY_SEX_SUBGROUP_ARM_TOTAL_DENOMINATOR",
                "severity": "critical", "blocking": True,
                "record_id": record_id,
                "message": "A sex-specific safety percentage uses total arm N as its denominator. Use the reported male/female subgroup N, or leave the denominator blank when it is not reported.",
            })
        if row.get("source_status") == "published_main_article_exact" and not row.get("source_page"):
            issues.append({
                "code": "POLICY_EXACT_WITHOUT_PAGE", "severity": "major", "blocking": False,
                "record_id": record_id, "message": "An exact-source record has no page locator.",
            })

    test_ids = [str(row.get("test_id")) for row in tests if row.get("test_id")]
    if len(test_ids) != len(set(test_ids)):
        issues.append({
            "code": "POLICY_DUPLICATE_TEST_ID", "severity": "critical", "blocking": True,
            "message": "Statistical-test identifiers are not unique.",
        })
    for row in tests:
        p_value = row.get("p_value")
        if isinstance(p_value, str) and any(symbol in p_value for symbol in ("<", "=", ">")):
            issues.append({
                "code": "POLICY_NONATOMIC_P_VALUE", "severity": "major", "blocking": False,
                "record_id": row.get("test_id"), "message": "p-value operator and number share one field.",
            })
    return issues


def apply_policy(dataset: dict[str, Any], root: Path) -> dict[str, Any]:
    """Attach the mandatory policy snapshot and non-destructive gate results."""
    snapshot = load_policy_bundle(root)
    issues = evaluate_dataset(dataset)
    dataset["system_extraction_policy"] = snapshot
    log = dataset.setdefault("validation_log", [])
    log[:] = [row for row in log if row.get("code") != "SYSTEM_EXTRACTION_SKILL"]
    log.append({
        "code": "SYSTEM_EXTRACTION_SKILL",
        "status": "REQUIRES_MANUAL_REVIEW" if issues else "APPLIED",
        "severity": "critical" if any(issue.get("blocking") for issue in issues) else "information",
        "message": (
            f"Automatic optimal-extraction skill applied; {len(issues)} representation issue(s) require review."
            if issues else
            "Automatic optimal-extraction skill and versioned statistical definitions applied; no representation-policy violation detected."
        ),
    })
    dataset["system_extraction_policy_issues"] = issues
    return {"snapshot": snapshot, "issues": issues, "blocking_issue_count": sum(bool(i.get("blocking")) for i in issues)}

