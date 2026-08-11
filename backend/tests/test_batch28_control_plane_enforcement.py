"""
Тесты фактического enforcement control plane (Батч 28).

Заменяет слабый test_batch27_reviewer_policy_files_exist, который проверял
только НАЛИЧИЕ файлов. Наличие файла ничего не доказывает: это ровно то
состояние, которое Reviewer.md §18 называет
"CONTROL PLANE IS DESCRIBED IN MARKDOWN" вместо "CONTROL PLANE EXISTS".

Здесь проверяется, что политика действительно классифицирует запрещённые
изменения как требующие человека.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = REPO_ROOT / "evolution" / "policy"
PROTECTED_PATHS = POLICY_DIR / "protected_paths.yaml"
RISK_CLASSIFICATION = POLICY_DIR / "risk_classification.yaml"
ENFORCER = REPO_ROOT / ".github" / "scripts" / "enforce_control_plane.py"


def run_enforcer(changed: list[str], tmp_path: Path) -> dict[str, str]:
    """Запускает enforcement-скрипт на списке путей, возвращает его outputs."""
    listing = tmp_path / "changed.txt"
    listing.write_text("\n".join(changed), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ENFORCER), str(listing)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    outputs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if line.startswith(("requires_human=", "max_risk=")):
            key, _, value = line.partition("=")
            outputs[key] = value
    assert outputs, f"Enforcer не вернул outputs. stdout:\n{result.stdout}\n{result.stderr}"
    return outputs


# ---------------------------------------------------------------------------
# Структурная целостность политики
# ---------------------------------------------------------------------------

def test_policy_files_exist():
    assert PROTECTED_PATHS.exists(), "protected_paths.yaml отсутствует"
    assert RISK_CLASSIFICATION.exists(), "risk_classification.yaml отсутствует"
    assert (REPO_ROOT / "CODEOWNERS").exists(), "CODEOWNERS отсутствует"
    assert ENFORCER.exists(), "Скрипт enforcement отсутствует — CI-барьера нет"


def test_ci_workflow_exists():
    """Без CI CODEOWNERS — декларация, а не enforcement (Reviewer.md §10)."""
    workflow = REPO_ROOT / ".github" / "workflows" / "control-plane-enforcement.yml"
    assert workflow.exists(), "Отсутствует CI workflow — третий барьер не реализован"


def test_default_policy_is_fail_safe():
    """Неперечисленный путь должен закрываться, а не открываться."""
    risk_cfg = yaml.safe_load(RISK_CLASSIFICATION.read_text(encoding="utf-8"))
    default = risk_cfg["resolution_rules"]["default_risk_for_unmatched"]
    assert default == "CRITICAL", (
        f"default_risk_for_unmatched={default}; должен быть CRITICAL (fail-safe)"
    )


def test_codeowners_has_catch_all():
    """
    В CODEOWNERS GitHub побеждает ПОСЛЕДНЕЕ совпадение, поэтому catch-all '*'
    обязан стоять первым, иначе неперечисленные файлы остаются без владельца.
    """
    lines = [
        line.strip()
        for line in (REPO_ROOT / "CODEOWNERS").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert lines, "CODEOWNERS пуст"
    assert lines[0].startswith("*"), (
        "Первым правилом CODEOWNERS должен быть catch-all '*' — "
        f"сейчас: {lines[0]}"
    )


def test_enforcement_dependency_graph_protected():
    """
    Защиты protected_paths.yaml недостаточно, если агент может изменить код,
    который его читает (Reviewer.md §5).
    """
    raw = PROTECTED_PATHS.read_text(encoding="utf-8")
    for required in ("evolution/mutation_api.py", "evolution/evaluator.py", ".github/"):
        assert required in raw, (
            f"{required} не защищён — возможен обход через изменение самого enforcement"
        )


# ---------------------------------------------------------------------------
# Фактическое поведение enforcement на запрещённых diff
# ---------------------------------------------------------------------------

FORBIDDEN_DIFFS = [
    pytest.param(["backend/app/services/qa/qa_inspector.py"], id="zone_r_qa"),
    pytest.param(["backend/app/services/mdr/mdr_generator.py"], id="zone_r_mdr"),
    pytest.param(["backend/app/services/cam/cam_engine.py"], id="zone_r_cam"),
    pytest.param(["shared/constants/thresholds.py"], id="zone_r_thresholds"),
    pytest.param(["backend/app/mcp/server.py"], id="zone_r_mcp_server"),
    pytest.param(["backend/app/db/schema.prisma"], id="zone_r_prisma"),
    pytest.param(["evolution/policy/protected_paths.yaml"], id="zone_p_self"),
    pytest.param(["evolution/evaluator.py"], id="zone_p_evaluator"),
    pytest.param(["evolution/mutation_api.py"], id="zone_p_mutation_api"),
    pytest.param(["CODEOWNERS"], id="zone_p_codeowners"),
    pytest.param([".github/workflows/control-plane-enforcement.yml"], id="zone_p_ci"),
    pytest.param(["backend/pyproject.toml"], id="zone_i_supply_chain"),
    pytest.param(["frontend/package.json"], id="zone_i_npm"),
    pytest.param(["backend/app/services/brand_new_module.py"], id="unmatched_failsafe"),
    pytest.param(["prompts/agents/qa_agent.md"], id="zone_e_but_high"),
]


@pytest.mark.parametrize("changed", FORBIDDEN_DIFFS)
def test_forbidden_diff_requires_human(changed, tmp_path):
    out = run_enforcer(changed, tmp_path)
    assert out["requires_human"] == "true", (
        f"{changed} НЕ заблокирован — автономный accept возможен. Дыра в политике."
    )


def test_mixed_diff_takes_max_risk(tmp_path):
    """Патч LOW+CRITICAL целиком считается CRITICAL (MAX_RISK_WINS)."""
    out = run_enforcer(
        ["frontend/components/TelemetryDock.tsx", "shared/constants/thresholds.py"],
        tmp_path,
    )
    assert out["max_risk"] == "CRITICAL"
    assert out["requires_human"] == "true"


def test_test_co_modification_escalates(tmp_path):
    """Правка теста вместе с продуктовым кодом обходит verification → HIGH."""
    out = run_enforcer(
        ["frontend/components/TelemetryDock.tsx", "backend/tests/test_batch7_qa.py"],
        tmp_path,
    )
    assert out["requires_human"] == "true"
    assert out["max_risk"] in {"HIGH", "CRITICAL"}


def test_pure_low_risk_is_autonomous(tmp_path):
    """
    Позитивный контроль: если бы всё блокировалось, тесты выше проходили бы
    тривиально. Разрешённое изменение должно проходить без человека.
    """
    out = run_enforcer(["frontend/components/TelemetryDock.tsx"], tmp_path)
    assert out["requires_human"] == "false"
    assert out["max_risk"] == "LOW"


def test_forbidden_metrics_declared():
    """Метрики, которыми агент управляет напрямую, не могут быть primary."""
    risk_cfg = yaml.safe_load(RISK_CLASSIFICATION.read_text(encoding="utf-8"))
    forbidden = set(risk_cfg.get("forbidden_primary_metrics", []))
    for metric in ("model_self_confidence", "number_of_tool_calls"):
        assert metric in forbidden, f"{metric} должен быть в forbidden_primary_metrics"
