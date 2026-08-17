# LISTA.md — Estado da Tarefa: Skill `/refactor-arch`

> Arquivo de estado do desafio "Skill de Auditoria e Refatoração Arquitetural".
> Atualizado continuamente. `CURRENT` aponta onde estou agora.

**Legenda:** `[ ]` pendente · `[~]` em andamento · `[x]` concluído · `[!]` bloqueado

**CURRENT:** 🔧 RODADA DE CORREÇÃO (feedback do professor) — playbook RP-06 ajustado + skill re-rodada no `task-manager-api`. Validado localmente. Falta commit/push (aguardando o usuário).

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

## M5 — Correção pós-feedback (guard de auth incompleto no `task-manager-api`)
> Feedback: o relatório marcava como HIGH a falta de auth em POST/PUT/DELETE de users/tasks/categories,
> mas a Fase 3 só protegeu `DELETE /users` e `GET /reports/summary`. Causa-raiz: RP-06 estava redigido
> como "guard admin/destructive endpoints" → só cobriu 2 rotas.
- [x] **Root cause na skill:** reescrito `RP-06` (playbook) → "guard EVERY write endpoint"; separa
      `require_auth` (escritas comuns) de `require_admin` (contas + relatórios); checklist de auto-verificação.
- [x] `SKILL.md` Fase 3: passo explícito "auth guard é tudo-ou-nada" + validação que checa 401 em cada escrita.
- [x] `antipattern-catalog.md` AP-09: nota de Fix apontando p/ guardar TODAS as escritas.
- [x] Sincronizado nas 3 cópias da skill (code-smells / ecommerce / task-manager) — md5 idêntico.
- [x] **Re-run no `task-manager-api`:** `middlewares/auth.py` ganhou `require_auth`; guardadas as 6 escritas
      de tasks/categories (`require_auth`) + as 3 de users e `/reports/summary` (`require_admin`).
- [x] Validação live (porta 5055): matriz completa passou — 401 sem token, 403 não-admin em rotas admin,
      200/201 com token; GET/login públicos; token adulterado → 401; sem erros no log; app sobe/encerra limpo.
- [x] `reports/audit-project-3.md` e `README.md` atualizados com o mapa de guards.
- [ ] Commit + push na `main` (aguardando o usuário).

## Log de progresso
- Exploração inicial dos 3 projetos concluída (stacks, domínios e anti-patterns mapeados).
- M0 concluído: `reports/` e `LISTA.md` criados.
- M5 (correção pós-feedback): RP-06 tornado "todo endpoint de escrita"; skill re-rodada e validada no task-manager-api.
