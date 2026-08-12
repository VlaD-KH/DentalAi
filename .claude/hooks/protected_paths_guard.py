#!/usr/bin/env python3
"""
PreToolUse hook (Edit|Write) — Zone-aware guard on top of Claude Code's own
permission system, mirroring evolution/policy/protected_paths.yaml at the
editor level, not just at CI level (.github/workflows/control-plane-enforcement.yml).

Это НЕ замена CI enforcement — git diff --name-only на PR остаётся
единственным авторитетным источником (см. protected_paths.yaml
"authority" и enforce_control_plane.py). Это просто более раннее
предупреждение человеку-разработчику в Phase 0 (human-supervised),
чтобы не узнавать о нарушении зоны только на этапе PR-проверки.

Поведение:
  - Zone P (policy plane, CODEOWNERS, .github/, evolution/evaluator.py, ...)
    -> DENY. Абсолютное правило: агент не может редактировать то, что его
       ограничивает (Reviewer.md §5). Никаких исключений на этом уровне.
  - Zone R (regulated core, клиническая логика) и Zone I (инфраструктура)
    -> ASK. Легитимно при человеко-контролируемой Phase 0 разработке —
       просто требует видимого подтверждения, а не тихого прохождения.
  - Zone T (тесты) -> ASK с напоминанием про TEST_CHANGE_ELEVATES_RISK
    (правку теста вместе с продуктовым кодом в одном патче риск-классификация
    поднимает до HIGH).
  - Zone E (evolvable product, allowlist) -> ALLOW, кроме путей из
    zone_e_but_high_risk (ASK).
  - Несопоставленный путь -> ASK (не DENY): default_policy.unmatched_path в
    YAML — PROTECTED для целей CI-классификации автономных патчей, но здесь
    человек и так за штурвалом, поэтому просто предупреждаем, а не блокируем
    легитимную разработку ещё не внесённых в allowlist Zone E путей
    (например backend/app/mcp/orchestration/, которого пока не существует).

Читает JSON из stdin (схема Claude Code PreToolUse hook), пишет решение в
stdout как hookSpecificOutput.permissionDecision.
"""
import json
import os
import re
import sys

REPO_ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
POLICY_PATH = os.path.join(REPO_ROOT, "evolution", "policy", "protected_paths.yaml")

ZONE_HEADER_RE = re.compile(r"^(zone_[a-z_]+|default_policy):\s*$")
ZONE_LABELS = {
    "zone_r_regulated_core": "R",
    "zone_p_policy_plane": "P",
    "zone_i_infrastructure": "I",
    "zone_t_tests": "T",
    "zone_e_evolvable_product": "E",
    "zone_e_but_high_risk": "E_HIGH_RISK",
}


def load_zone_paths():
    """
    Пытается использовать pyyaml, если доступен; иначе — минимальный
    построчный парсер (достаточен для плоской структуры этого конкретного
    файла: top-level zone_* ключ переключает текущую зону, любая строка вида
    `- "путь"` / `- 'путь'` / `- path: "путь"` под ней добавляется в эту зону).
    Не пытается парсить произвольный YAML — только protected_paths.yaml.
    """
    zones = {}  # path -> zone_label
    if not os.path.exists(POLICY_PATH):
        return zones

    try:
        import yaml  # type: ignore

        with open(POLICY_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        def walk(node, zone_label):
            if isinstance(node, dict):
                for v in node.values():
                    walk(v, zone_label)
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, str):
                        zones[item] = zone_label
                    elif isinstance(item, dict) and "path" in item:
                        zones[item["path"]] = zone_label
                    else:
                        walk(item, zone_label)

        for key, label in ZONE_LABELS.items():
            if key in data:
                walk(data[key], label)
        return zones
    except Exception:
        pass

    # Фолбэк без pyyaml
    current_zone = None
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            header = ZONE_HEADER_RE.match(stripped)
            if header:
                key = header.group(1)
                current_zone = ZONE_LABELS.get(key)
                continue
            if current_zone is None:
                continue
            m = re.match(r'^-\s+(?:path:\s*)?["\']([^"\']+)["\']', stripped)
            if m:
                zones[m.group(1)] = current_zone
    return zones


def classify(rel_path: str, zones: dict):
    """MOST_SPECIFIC_PATH_WINS: самый длинный совпавший префикс/точное имя файла побеждает."""
    best_match = None
    best_zone = None
    for pattern, zone in zones.items():
        # Точное совпадение файла
        if pattern == rel_path:
            if best_match is None or len(pattern) > len(best_match):
                best_match, best_zone = pattern, zone
            continue
        # Директория-префикс
        if pattern.endswith("/") and rel_path.startswith(pattern):
            if best_match is None or len(pattern) > len(best_match):
                best_match, best_zone = pattern, zone
    return best_zone, best_match


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # не наш формат — пропускаем, ничего не решаем

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        sys.exit(0)

    try:
        rel_path = os.path.relpath(file_path, REPO_ROOT).replace(os.sep, "/")
    except Exception:
        rel_path = file_path

    zones = load_zone_paths()
    zone, matched = classify(rel_path, zones)

    decision = None
    reason = None

    if zone == "P":
        decision = "deny"
        reason = (
            f"Zone P (Policy Plane): '{rel_path}' совпадает с '{matched}'. "
            "Агент не может изменять механизм, который его ограничивает "
            "(Reviewer.md §5, evolution/policy/protected_paths.yaml). "
            "Изменения только через PR с approval CODEOWNERS."
        )
    elif zone == "R":
        decision = "ask"
        reason = (
            f"Zone R (Regulated Core / MDR EU 2017/745): '{rel_path}' совпадает с '{matched}'. "
            "Клинически значимый код — подтвердите осознанно (Phase 0, human-supervised)."
        )
    elif zone == "I":
        decision = "ask"
        reason = (
            f"Zone I (Infrastructure): '{rel_path}' совпадает с '{matched}'. "
            "Изменение инфраструктуры/зависимостей = вектор произвольного выполнения кода — подтвердите."
        )
    elif zone == "T":
        decision = "ask"
        reason = (
            f"Zone T (Tests): '{rel_path}' совпадает с '{matched}'. "
            "TEST_CHANGE_ELEVATES_RISK: правка теста вместе с продуктовым кодом в одном патче "
            "поднимает риск до HIGH (protected_paths.yaml)."
        )
    elif zone == "E_HIGH_RISK":
        decision = "ask"
        reason = (
            f"Zone E, но high-risk: '{rel_path}' совпадает с '{matched}'. "
            "Физически Evolvable Product, но принадлежность к Zone E не означает auto-accept (Reviewer.md §6)."
        )
    elif zone == "E":
        sys.exit(0)  # allow, тихо
    else:
        decision = "ask"
        reason = (
            f"'{rel_path}' не сопоставлен ни одной зоне в protected_paths.yaml. "
            "default_policy.unmatched_path = PROTECTED для CI-классификации автономных патчей; "
            "здесь просто предупреждение — подтвердите, что путь всё ещё не внесён в allowlist сознательно."
        )

    if decision:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason,
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
