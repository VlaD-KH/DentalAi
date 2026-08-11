Ниже — роль такого ревьюера в той архитектуре, которая следует из DentalAi ТЗ и исходной спецификации Ouroboros. Ключевой момент: ревьюер здесь не является ещё одним разработчиком self-evolution kernel. Он является **внешним владельцем security/policy boundary**, а LLM используется только как инструмент анализа и подготовки черновика.

ТЗ прямо требует, чтобы Zone R и Zone P не контролировались самим агентом: защита должна обеспечиваться `CODEOWNERS`, branch protection и CI enforcement, а не prompt-инструкциями. Исходная архитектура Ouroboros формулирует тот же принцип шире: policy/evaluation plane должен быть внешним по отношению к mutable product plane, а protected paths должны enforced-иться вне модели.

# **1\. Кто такой этот Reviewer**

Рабочее определение:

> **Independent Control-Plane Reviewer** — человек, ответственный за создание, проверку и первоначальную фиксацию неизменяемых правил эволюционного контура DentalAi, с использованием отдельной LLM в качестве аналитического/генеративного инструмента, но без передачи ей полномочий по применению этих правил.

Его задача не в том, чтобы решить:

> «Как лучше написать `protected_paths.yaml`?»

Его задача:

> «Какие ограничения self-evolution должны существовать независимо от того, что впоследствии скажет или сделает харнас?»

Это принципиальное различие.

В Ouroboros policy должна быть enforcement layer, а не текстовой договорённостью с моделью; сам prompt не является security boundary.

---

# **2\. Почему Reviewer должен быть отдельным от харнаса**

Схема должна выглядеть так:

                 ┌──────────────────────────┐  
                  │ Human Reviewer           │  
                  │ Control-Plane Owner      │  
                  └────────────┬─────────────┘  
                               │  
                    uses as assistant  
                               ▼  
                  ┌──────────────────────────┐  
                  │ Independent LLM          │  
                  │ analysis / drafting      │  
                  └────────────┬─────────────┘  
                               │  
                       draft / critique  
                               ▼  
                  ┌──────────────────────────┐  
                  │ Human review              │  
                  │ \+ repository inspection   │  
                  └────────────┬─────────────┘  
                               │  
                          approved files  
                               ▼  
             ┌────────────────────────────────────┐  
             │ GitHub / external enforcement      │  
             │                                    │  
             │ protected\_paths.yaml                │  
             │ risk\_classification.yaml            │  
             │ CODEOWNERS                          │  
             │ branch protection                   │  
             │ CI reject rules                     │  
             └────────────────────────────────────┘  
                               ▲  
                               │  
                      cannot be rewritten by  
                      self-evolution harness  
                               │  
                         ┌─────┴─────┐  
                         │  Harnas   │  
                         └───────────┘

То есть **LLM не является владельцем policy**, а Reviewer не является «ручным executor'ом» харнаса. Он устанавливает исходные границы, после чего сам харнас работает внутри них.

---

# **3\. Что именно Reviewer должен создать**

Минимальный пакет Phase 1:

evolution/  
└── policy/  
    ├── protected\_paths.yaml  
    └── risk\_classification.yaml

CODEOWNERS

GitHub branch protection:  
main

Это напрямую соответствует структуре DentalAi ТЗ. Там `protected_paths.yaml` предназначен для Zone R \+ Zone P, а `risk_classification.yaml` содержит матрицу риска и режима изменения.

Но фактически Reviewer отвечает не просто за существование этих файлов, а за **согласованность четырёх слоёв**:

1\. protected\_paths.yaml  
          ↓  
2\. risk\_classification.yaml  
          ↓  
3\. CODEOWNERS  
          ↓  
4\. GitHub branch protection \+ CI enforcement

Если хотя бы один слой слабее остальных, control plane может оказаться формальным.

---

# **4\. Первая ответственность: восстановить фактическую структуру репозитория**

Reviewer не должен писать `protected_paths.yaml`, исходя только из ТЗ.

Сначала он должен установить:

> «Какие реальные файлы и каталоги существуют сейчас в `VlaD-KH/DentalAi`?»

Для этого допустимы:

* просмотр repository tree;  
* Git history;  
* существующие CI workflows;  
* существующий `CODEOWNERS`, если он уже есть;  
* существующие permission/automation-файлы;  
* фактическое содержимое директорий, перечисленных в ТЗ.

Причина проста: ТЗ содержит **нормативную архитектуру**, а repository содержит **фактическую поверхность атаки**.

В ТЗ Zone R явно включает geometry, crown generation, CAM, QA, MDR, segmentation, thresholds, Prisma schema и `bible.md`; Zone P — `evolution/policy`, `evolution/metrics` и risk classification.

Reviewer должен проверить обе вещи:

SPECIFIED PATH  
      vs  
ACTUAL PATH

и установить расхождения.

### **Например**

Если в ТЗ написано:

backend/app/services/geometry/

Reviewer обязан проверить:

* существует ли каталог;  
* есть ли альтернативные пути;  
* не вынесена ли часть geometry logic в другое место;  
* нет ли symlink/import boundary;  
* не существует ли ещё одного критичного implementation path.

Именно поэтому Reviewer должен иметь право **добавить путь в защиту**, если это необходимо для фактического containment, даже если конкретное имя отсутствует в черновике ТЗ.

При этом он не должен сам произвольно расширять scope self-evolution: его функция — защищать control plane и regulated core, а не придумывать новые mutable области.

---

# **5\. Вторая ответственность: написать `protected_paths.yaml`**

Это главный артефакт Reviewer.

Его смысл:

> определить filesystem/repository boundaries, которые evolution kernel не может автономно изменять.

ТЗ формально разделяет:

ZONE R \= REGULATED CORE  
ZONE P \= POLICY / EVALUATION PLANE  
ZONE E \= EVOLVABLE PRODUCT PLANE

и прямо говорит, что Zone R и Zone P находятся вне autonomous mutation.

Reviewer должен гарантировать, что YAML реализует именно это разделение.

### **В его проверку входит**

**Полнота.**

Ни один критический путь Zone R/P не должен отсутствовать.

**Отсутствие двусмысленности.**

Например, если защищён:

evolution/policy/

не должно существовать другого пути вроде:

config/evolution\_policy/

который фактически хранит ту же policy.

**Нет обхода через файл более высокого уровня.**

Например, защита:

evolution/policy/protected\_paths.yaml

недостаточна, если сам агент может изменить:

evolution/mutation\_api.py

и удалить проверку этого файла.

Поэтому Reviewer должен мыслить не только категориями файлов, но и категориями **enforcement dependency graph**.

---

# **6\. Третья ответственность: написать `risk_classification.yaml`**

Этот файл отвечает уже не на вопрос:

> «Можно ли изменять файл?»

а на вопрос:

> «Какой уровень автономии допустим для изменения?»

В DentalAi предусмотрена такая шкала:

LOW  
MEDIUM  
HIGH  
CRITICAL

Например:

TelemetryDock.tsx                → LOW  
AgentSwarmLogger.tsx              → LOW–MEDIUM  
MCP orchestration                → MEDIUM  
orchestrator.md                  → MEDIUM  
qa\_agent.md / cam\_agent.md       → HIGH  
Zone R                            → CRITICAL

Причём ТЗ специально подчёркивает интересный случай:

qa\_agent.md  
cam\_agent.md

физически остаются в Zone E, но risk \= HIGH, потому что изменение prompt может влиять на безопасность изделия.

Reviewer должен проверить, что risk classification **не превращает физическую принадлежность к Zone E в автоматическое право на auto-accept**.

---

# **7\. Как Reviewer должен использовать вторую LLM**

Здесь я бы ввёл жёсткое правило:

> **Independent LLM может готовить, критиковать и искать противоречия, но не может самостоятельно установить policy как окончательную.**

То есть допустимый цикл:

Reviewer  
   ↓  
Independent LLM  
   ↓  
draft  
   ↓  
Independent LLM  
   ↓  
adversarial critique  
   ↓  
Reviewer  
   ↓  
final decision

Хорошая практика — использовать **две логические роли внутри независимой модели**:

### **Режим A — Architect / Author**

LLM получает:

* DentalAi TZ;  
* repository tree;  
* конкретные существующие policy/CI-файлы;  
* ограничения роли Reviewer.

Её задача:

> предложить первый вариант `protected_paths.yaml`, `risk_classification.yaml`, `CODEOWNERS` и CI enforcement.

### **Режим B — Adversarial Auditor**

Та же или другая независимая модель получает **готовый draft**, но не должна исходить из того, что он правильный.

Её задача:

Find bypasses.  
Find omissions.  
Find contradictions.  
Find paths not covered.  
Find policy mutation vectors.  
Find privilege escalation.  
Find metric/evaluator loopholes.  
Find inconsistencies between YAML / CODEOWNERS / CI.

Это намного полезнее, чем просто попросить LLM:

> «Напиши мне правильный YAML».

---

# **8\. Что LLM категорически не должна решать самостоятельно**

Reviewer должен заранее исключить из полномочий модели вопросы типа:

«Можно ли разрешить autonomous mutation для QA?»  
«Нужен ли CAM в MEDIUM или HIGH?»  
«Можно ли убрать этот protected path?»  
«Можно ли считать файл policy частью Zone E?»  
«Можно ли дать bot merge permissions?»

LLM может дать аргументацию.

Она не должна являться authority.

Иначе получается:

LLM  
 ↓  
defines policy  
 ↓  
same system  
 ↓  
operates under policy

а это именно тот класс circular trust, от которого архитектура пытается уйти.

В исходном документе прямо установлено:

Proposer ≠ Evaluator  
Evaluator ≠ Policy editor  
Mutable product ≠ Control plane

Для Reviewer логика должна быть ещё строже:

Evolution Agent ≠ Policy Author  
Evolution Agent ≠ Policy Approver  
Independent LLM ≠ Policy Authority  
Human Reviewer \= Policy Authority

---

# **9\. Четвёртая ответственность: проверить `CODEOWNERS`**

`CODEOWNERS` — это уже не документирование политики, а механизм enforcement.

Reviewer должен проверить:

Zone R → human owner  
Zone P → human owner

и принципиально:

НЕ:  
Zone R → bot  
Zone P → evolution-agent

ТЗ прямо требует human approval для защищённых путей и указывает, что kernel не имеет merge-прав, а может лишь создавать PR.

Reviewer должен проверить не только сам текст `CODEOWNERS`, но и вопрос:

> «А может ли бот фактически обойти его?»

Например, через:

* direct push;  
* privileged GitHub App;  
* отдельный service account;  
* workflow с `GITHUB_TOKEN`;  
* automation, имеющий право approve/merge;  
* self-approval PR;  
* другой branch, который затем автоматически вливается.

---

# **10\. Пятая ответственность: проверить branch protection**

Это принципиально важно.

`CODEOWNERS` без branch protection — это **не enforcement**, а декларация.

Reviewer должен подтвердить, что для `main`:

PR required  
review required  
CODEOWNER approval required  
direct push restricted  
bot merge unavailable

И особенно:

> человек не должен утверждать изменение только потому, что бот сам создал его и сам его одобрил.

В ТЗ прямо сказано, что merge всегда делает человек и kernel имеет только `open_pull_request`.

---

# **11\. Шестая ответственность: обеспечить CI как третий независимый барьер**

Это очень важное отличие от простого `CODEOWNERS`.

Нужна цепочка:

LLM  
 ↓  
candidate patch  
 ↓  
CI  
 ↓  
detect protected diff  
 ↓  
requires\_human \= true  
 ↓  
NO AUTONOMOUS ACCEPT

ТЗ предписывает именно это: CI должен анализировать `git diff --name-only`, и при касании Zone R/P кандидат должен автоматически считаться требующим человека, независимо от verification/evaluation результата.

То есть Reviewer должен проверить, что enforcement работает **по фактическому diff**, а не по заявлению модели:

proposal.zone \= E

Потому что модель может ошибиться.

Авторитетным должен быть:

git diff \--name-only

а не:

{  
  "zone": "E"  
}

---

# **12\. Особое задание Reviewer: искать обходы через серию маленьких патчей**

Это одна из самых важных частей роли.

Недостаточно проверить:

patch A запрещён

Нужно проверить:

patch A разрешён  
patch B разрешён  
patch C разрешён  
...  
A+B+C → фактически переписывают policy

Именно такую проблему исходная спецификация называет «растворением immune system через серию мелких изменений».

Reviewer должен проводить **compositional security review**:

Can a sequence of individually allowed mutations  
produce a forbidden final state?

Например:

Patch 1:  
modify orchestration

Patch 2:  
modify prompt

Patch 3:  
modify evaluator caller

Patch 4:  
modify config

Result:  
policy enforcement is effectively bypassed

Если это возможно — policy недостаточна.

---

# **13\. Седьмая ответственность: проверить, что evaluator действительно вне зоны доверия харнаса**

DentalAi специально снимает проблему `Proposer == Evaluator` тем, что `evaluator.py` должен быть детерминированным, без LLM-вызова. Он сравнивает заранее определённые baseline/candidate telemetry и принимает решение по формуле.

Поэтому Reviewer должен проверить:

agent  
   ↓  
candidate  
   ↓  
evaluator

но не:

agent  
   ↓  
изменяет evaluator  
   ↓  
evaluator  
   ↓  
говорит, что agent хорош

Особенно важно проверить:

metric\_definition.yaml  
success\_threshold  
guardrails  
minimum\_sample

не могут быть изменены той же evolution transaction.

Это требование отдельно сформулировано в Ouroboros.

---

# **14\. Восьмая ответственность: проверить соответствие risk → action**

Reviewer должен получить таблицу вида:

| Risk | Autonomous mutation | Evaluation | Human approval |
| ----- | ----- | ----- | ----- |
| LOW | да | да | нет при guardrails |
| MEDIUM | ограниченно | synthetic/canary | да/ sampling |
| HIGH | proposal only / candidate | да | обязательно |
| CRITICAL | нет | — | обычный human process |

Это должно соответствовать реальной реализации.

Нельзя допустить рассинхрон:

risk\_classification.yaml:  
HIGH

mutation\_api.py:  
allowed

CI:  
auto-accept

В таком случае policy на бумаге HIGH, а фактическая policy LOW.

---

# **15\. Что Reviewer не должен делать**

Это не менее важно, чем список его обязанностей.

Reviewer **не должен**:

### **Не должен**

* разрабатывать сам Self-Evolution Kernel;  
* писать `mutation_api.py` как часть этой роли;  
* менять харнас;  
* давать харнасу доступ к policy до её фиксации;  
* разрешать себе «временно» ослабить protection;  
* утверждать собственные изменения автоматически;  
* использовать ту же LLM/agent, которая потом будет работать под этой policy, для окончательной авторизации policy;  
* превращать risk classification в рекомендацию вместо enforcement.

### **И особенно**

Reviewer не должен смешивать:

"это удобно для разработки"

с:

"это разрешено control plane"

---

# **16\. Что является главным продуктом работы Reviewer**

Не три файла.

Фактически результатом является вот это:

CONTROL-PLANE BASELINE

с пятью свойствами:

### **1\. Completeness**

Все критические пути покрыты.

### **2\. Consistency**

protected\_paths  
    ↔ risk\_classification  
    ↔ CODEOWNERS  
    ↔ CI  
    ↔ branch protection

не противоречат друг другу.

### **3\. Non-self-reference**

Харнас не может изменить механизм, который ограничивает его самого.

### **4\. Enforceability**

Ограничения проверяются платформой/CI, а не prompt'ом.

### **5\. Auditability**

Можно восстановить:

кто создал policy  
когда  
на основе какого commit  
кто её проверил  
какая версия policy действует  
какие правила были утверждены

---

# **17\. Как должна выглядеть работа Reviewer с LLM**

Я бы зафиксировал следующий протокол.

PHASE A — READ  
Reviewer → LLM  
    TZ  
    repository tree  
    relevant files  
    existing CI  
    existing permissions

PHASE B — MODEL  
LLM  
    reconstructs boundaries  
    identifies paths  
    identifies risks  
    identifies enforcement dependencies

PHASE C — DRAFT  
LLM  
    produces:  
      protected\_paths.yaml  
      risk\_classification.yaml  
      CODEOWNERS proposal  
      CI protection proposal

PHASE D — ATTACK  
Independent LLM  
    attacks draft:  
      bypasses  
      omissions  
      privilege escalation  
      policy mutation  
      metric gaming  
      path aliasing  
      workflow bypass

PHASE E — HUMAN DECISION  
Reviewer  
    accepts / rejects / modifies

PHASE F — INSTALL  
Human  
    commits files  
    configures branch protection  
    configures repository permissions

PHASE G — VERIFY  
Human \+ CI  
    deliberately test forbidden diffs  
    verify autonomous reject  
    verify human approval requirement

PHASE H — FREEZE  
Only after successful verification:  
    hand TZ to harnas

И только после этого выполняется шаг, который предлагает ваше исходное рассуждение: харнасу передаётся `DentalAi_Self_Evolution_Kernel_TZ.md`. ТЗ само говорит, что Phase 1 начинается с `protected_paths.yaml`, `mutation_api.py`, CODEOWNERS и branch protection, а Phase 3 ограничивается сначала LOW-risk Zone E.

---

# **18\. Критерий «Reviewer закончил работу»**

Я бы не использовал критерий:

> «YAML-файлы написаны».

Правильный Definition of Ready для подключения харнаса:

\[ \] Zone R определена  
\[ \] Zone P определена  
\[ \] Zone E явно отделена  
\[ \] protected\_paths.yaml создан человеком  
\[ \] risk\_classification.yaml создан человеком  
\[ \] CODEOWNERS создан/проверен человеком  
\[ \] main защищён  
\[ \] bot не имеет merge authority  
\[ \] protected diff автоматически блокируется  
\[ \] policy/evaluator нельзя менять обычной evolution transaction  
\[ \] CI проверяет фактический diff  
\[ \] серия мелких патчей не позволяет обойти policy  
\[ \] независимая LLM провела adversarial review  
\[ \] Reviewer разрешил baseline  
\[ \] baseline commit зафиксирован

Только после этого можно честно сказать:

CONTROL PLANE EXISTS

а не просто:

CONTROL PLANE IS DESCRIBED IN MARKDOWN

---

# **19\. Самая важная граница роли**

Я бы сформулировал её одной фразой для отдельного регламента:

> **Reviewer отвечает не за то, чтобы self-evolution работал, а за то, чтобы до запуска self-evolution были технически зафиксированы пределы того, что self-evolution никогда не сможет изменить самостоятельно.**

Это полностью согласуется с архитектурной границей DentalAi: Zone R и Zone P остаются вне автономной мутации, а первый реальный evolutionary loop запускается только на Zone E / LOW risk.

И это также соответствует центральному принципу исходной спецификации: **self-modification — лишь capability; self-evolution появляется только при наличии evidence, independent evaluation, rollback и памяти результатов.**

### **В практическом смысле**

Получается не:

Человек  
  ↓  
LLM пишет policy  
  ↓  
Харнас использует policy

а:

Человек  
  ↓  
Independent LLM помогает проанализировать  
  ↓  
Human Reviewer принимает security decisions  
  ↓  
External GitHub/CI enforcement  
  ↓  
Protected control plane  
  ↓  
Харнас работает внутри заранее заданного коридора

Именно **последний вариант** я бы считал корректной моделью для DentalAi.

