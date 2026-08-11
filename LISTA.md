# LISTA.md — Estado da Tarefa: Skill `/refactor-arch`

> Arquivo de estado do desafio "Skill de Auditoria e Refatoração Arquitetural".
> Atualizado continuamente. `CURRENT` aponta onde estou agora.

**Legenda:** `[ ]` pendente · `[~]` em andamento · `[x]` concluído · `[!]` bloqueado

**CURRENT:** ✅ DESAFIO CONCLUÍDO — tudo commitado e pushado na main (último: 2e65791).

**Decisões fixadas:** execução um projeto por vez · commits na `main` + push · layout `src/` MVC.

---

## M0 — Preparação
- [x] Criar `reports/`
- [x] Criar `LISTA.md`
- [x] Consolidar análise manual dos 3 projetos (exploração feita — base p/ README seção A)

## M1 — Construir a skill + Projeto 1 (`code-smells-project` · Python/Flask)
### Skill
- [x] `SKILL.md` (frontmatter + 3 fases)
- [x] `references/project-analysis.md`
- [x] `references/antipattern-catalog.md` (18 anti-patterns, severidade distribuída, inclui deprecated APIs)
- [x] `references/audit-report-template.md`
- [x] `references/mvc-architecture-guidelines.md`
- [x] `references/refactoring-playbook.md` (12 transformações antes/depois)
### Execução Projeto 1
- [x] Fase 1: stack detectada (Python/Flask 3.1.1, e-commerce, 4 arquivos)
- [x] Fase 2: 16 findings (5 CRITICAL, 4 HIGH, 4 MEDIUM, 3 LOW), ordenado, com file:line
- [x] GATE Fase 2->3: confirmado pelo usuário ("proceda para fase 3")
- [x] Fase 3: estrutura `src/` MVC criada (config/models/views/controllers/services/middlewares)
- [x] Validação: app sobe + 17 endpoints testados (login/hash, transação, JOIN, relatório, admin gated, SQLi neutralizada)
- [x] `reports/audit-project-1.md` salvo
- [x] Commit na `main` + push (1a52ab2)
- [~] CHECK-IN com usuário

## M2 — Projeto 2 (`ecommerce-api-legacy` · Node/Express)
- [x] Copiar `.claude/skills/refactor-arch/` para o projeto
- [x] Fase 1: stack detectada (Node/Express 4.x, LMS/checkout, 3 arquivos)
- [x] Fase 2: 16 findings (5 CRITICAL, 5 HIGH, 3 MEDIUM, 3 LOW), com file:line
- [x] GATE Fase 2->3: confirmado ("proceed")
- [x] Fase 3: `src/` MVC criada (config/models/routes/controllers/services/middlewares; sqlite3 promisificado, async/await)
- [x] Validação: npm install + boot + endpoints (checkout ok/recusado, auth 401, JOIN report, cascata delete, sem vazamento de cartão/chave)
- [x] `reports/audit-project-2.md` salvo
- [x] Commit na `main` + push (62bfa52)
- [~] CHECK-IN com usuário

## M3 — Projeto 3 (`task-manager-api` · Python/Flask+SQLAlchemy)
- [x] Copiar `.claude/skills/refactor-arch/` para o projeto
- [x] Fase 1: stack detectada (Python/Flask 3.0.0 + SQLAlchemy, Task Manager, 15 .py)
- [x] Fase 2: 17 findings (5 CRITICAL, 5 HIGH, 4 MEDIUM, 3 LOW), com file:line
- [x] GATE Fase 2->3: confirmado
- [x] Fase 3: `src/` MVC (config/models/views/controllers/services/utils/middlewares; services/utils viraram camada real e usada)
- [x] Validação: seed + boot + endpoints (auth admin 401/403/200, N+1→eager/agregado, cascata delete, token assinado, sem 500, sem deprecation)
- [x] `reports/audit-project-3.md` salvo
- [x] Commit na `main` + push (5a8682c)
- [x] CHECK-IN com usuário

## M4 — Finalização
- [x] README.md seções A/B/C/D preenchidas (enunciado original preservado abaixo)
- [x] Checklist de aceite marcado (3/3 projetos)
- [x] Commit final na `main` + push (2e65791)

---

## Log de progresso
- Exploração inicial dos 3 projetos concluída (stacks, domínios e anti-patterns mapeados).
- M0 concluído: `reports/` e `LISTA.md` criados.
