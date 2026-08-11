# Установка Control Plane — быстрый старт

Структура этого пакета повторяет структуру репозитория DentalAi.
Копировать в корень репозитория с сохранением путей.

```
CODEOWNERS                                              → корень репо
evolution/policy/protected_paths.yaml                   → заменяет v1.0
evolution/policy/risk_classification.yaml               → заменяет v1.0
evolution/policy/BRANCH_PROTECTION.md                   → новый
.github/workflows/control-plane-enforcement.yml         → новый (CI-барьер)
.github/scripts/enforce_control_plane.py                → новый
backend/tests/test_batch28_control_plane_enforcement.py → новый
DentalAi_MASTER_TZ_v2.md                                → документация
```

Одной командой из корня репозитория:

```bash
cp -r <путь_к_пакету>/{CODEOWNERS,evolution,.github,backend} .
python -m pytest backend/tests/test_batch28_control_plane_enforcement.py -q
```

Ожидаемо: 24 passed.

Далее — Часть VI документа DentalAi_MASTER_TZ_v2.md, начиная с Шага 2.

ВАЖНО: `.github/workflows/` и `evolution/policy/` создаёт человек.
Агенту эти файлы недоступны для изменения — это и есть суть control plane.
