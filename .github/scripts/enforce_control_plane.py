#!/usr/bin/env python3
"""
Control Plane Enforcement — классификация фактического diff.

Читает:
    evolution/policy/protected_paths.yaml
    evolution/policy/risk_classification.yaml

Получает на вход файл со списком изменённых путей (git diff --name-only).

Выводит в GITHUB_OUTPUT:
    requires_human  — true/false
    max_risk        — LOW | MEDIUM | HIGH | CRITICAL

Принципы (Reviewer.md §11, §14):
  * Авторитетен git diff, а не заявление модели о своей зоне.
  * default_risk_for_unmatched = CRITICAL (fail-safe).
  * MAX_RISK_WINS для смешанного diff.
  * MOST_SPECIFIC_PATH_WINS при пересечении правил.

Этот скрипт находится в Zone P и не может быть изменён агентом эволюции.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

POLICY_DIR = Path("evolution/policy")
PROTECTED = POLICY_DIR / "protected_paths.yaml"
RISK = POLICY_DIR / "risk_classification.yaml"

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
AUTONOMOUS_OK = {"LOW"}  # только LOW может быть принят без человека


def load_yaml(path: Path) -> dict:
    if not path.exists():
        # Отсутствие policy-файла — не повод разрешить: fail closed.
        print(f"::error::Policy file missing: {path}. Fail closed.")
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def flatten_zone(node) -> list[str]:
    """Zone-секции могут быть списком либо словарём групп со списками."""
    out: list[str] = []
    if isinstance(node, list):
        for item in node:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict) and "path" in item:
                out.append(item["path"])
    elif isinstance(node, dict):
        for value in node.values():
            out.extend(flatten_zone(value))
    return out


def path_matches(changed: str, rule: str) -> bool:
    """Директория-правило покрывает всё поддерево; файл-правило — точное совпадение."""
    if rule.endswith("/"):
        return changed.startswith(rule)
    return changed == rule or changed.startswith(rule + "/")


def classify(changed: str, matrix: list[dict], default_risk: str) -> tuple[str, str]:
    """Возвращает (risk, rationale) по правилу MOST_SPECIFIC_PATH_WINS."""
    best_rule, best_len = None, -1
    for entry in matrix:
        rule = entry.get("path", "")
        if rule and path_matches(changed, rule) and len(rule) > best_len:
            best_rule, best_len = entry, len(rule)
    if best_rule is None:
        return default_risk, "unmatched → default_risk_for_unmatched (fail-safe)"
    return best_rule.get("risk", default_risk), best_rule.get("rationale", "")


def main() -> int:
    if len(sys.argv) < 2:
        print("::error::Usage: enforce_control_plane.py <changed_files.txt>")
        return 1

    changed_files = [
        line.strip()
        for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not changed_files:
        print("No changed files. Nothing to enforce.")
        write_output(requires_human="false", max_risk="LOW")
        return 0

    protected_cfg = load_yaml(PROTECTED)
    risk_cfg = load_yaml(RISK)

    resolution = risk_cfg.get("resolution_rules", {})
    default_risk = resolution.get("default_risk_for_unmatched", "CRITICAL")
    matrix = risk_cfg.get("matrix", [])

    protected_paths: list[str] = []
    for zone_key in (
        "zone_r_regulated_core",
        "zone_p_policy_plane",
        "zone_i_infrastructure",
    ):
        protected_paths.extend(flatten_zone(protected_cfg.get(zone_key, [])))

    zone_e_paths = flatten_zone(protected_cfg.get("zone_e_evolvable_product", []))
    high_risk_e = [
        item["path"]
        for item in protected_cfg.get("zone_e_but_high_risk", [])
        if isinstance(item, dict) and "path" in item
    ]

    max_risk = "LOW"
    requires_human = False
    report: list[str] = []

    touches_product = any(
        f.startswith(("backend/app/", "frontend/", "shared/")) for f in changed_files
    )
    touches_tests = any(f.startswith("backend/tests/") for f in changed_files)

    for changed in changed_files:
        risk, rationale = classify(changed, matrix, default_risk)

        is_protected = any(path_matches(changed, p) for p in protected_paths)
        in_zone_e = any(path_matches(changed, p) for p in zone_e_paths)

        # Явный HIGH для промптов QA/CAM, даже если формально в Zone E
        if any(path_matches(changed, p) for p in high_risk_e):
            risk = "HIGH"
            rationale = "Zone E, но HIGH: влияет на безопасность изделия"

        # Zone T: тесты вместе с продуктовым кодом → HIGH
        if changed.startswith("backend/tests/") and touches_product:
            risk = "HIGH"
            rationale = "Тесты изменены вместе с продуктовым кодом (обход verification)"

        # Защищённый путь всегда требует человека
        if is_protected:
            requires_human = True
            if RISK_ORDER[risk] < RISK_ORDER["CRITICAL"]:
                risk = "CRITICAL"
                rationale = "path in protected zone (R/P/I)"

        # Не в Zone E и не защищён явно → fail-safe
        if not in_zone_e and not is_protected:
            requires_human = True

        if risk not in AUTONOMOUS_OK:
            requires_human = True

        if RISK_ORDER[risk] > RISK_ORDER[max_risk]:
            max_risk = risk

        flag = "BLOCK" if risk not in AUTONOMOUS_OK else "ok   "
        report.append(f"  [{flag}] {risk:<8} {changed}  — {rationale}")

    print("=" * 78)
    print("CONTROL PLANE ENFORCEMENT REPORT")
    print("=" * 78)
    print(f"Changed files : {len(changed_files)}")
    print(f"Touches tests : {touches_tests}")
    print(f"Max risk      : {max_risk}")
    print(f"Requires human: {requires_human}")
    print("-" * 78)
    print("\n".join(report))
    print("=" * 78)

    write_output(
        requires_human="true" if requires_human else "false",
        max_risk=max_risk,
    )
    return 0


def write_output(**kwargs: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        for key, value in kwargs.items():
            print(f"{key}={value}")
        return
    with open(out, "a", encoding="utf-8") as fh:
        for key, value in kwargs.items():
            fh.write(f"{key}={value}\n")


if __name__ == "__main__":
    raise SystemExit(main())
