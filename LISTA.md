# LISTA.md — Estado da Tarefa: Skill `/refactor-arch`

> Arquivo de estado do desafio "Skill de Auditoria e Refatoração Arquitetural".
> Atualizado continuamente. `CURRENT` aponta onde estou agora.

**Legenda:** `[ ]` pendente · `[~]` em andamento · `[x]` concluído · `[!]` bloqueado

**CURRENT:** M1 — Projeto 1 validado; commitando e fazendo check-in

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
- [~] Commit na `main` + push
- [~] CHECK-IN com usuário

## M2 — Projeto 2 (`ecommerce-api-legacy` · Node/Express)
- [ ] Copiar `.claude/skills/refactor-arch/` para o projeto
- [ ] Fase 1: stack detectada (Node/Express, LMS/checkout)
- [ ] Fase 2: >=5 findings, >=1 CRITICAL/HIGH, com file:line
- [ ] GATE Fase 2->3: confirmação
- [ ] Fase 3: `src/` MVC criada
- [ ] Validação: `npm install` + boot + endpoints
- [ ] `reports/audit-project-2.md` salvo
- [ ] Commit na `main` + push
- [ ] CHECK-IN com usuário

## M3 — Projeto 3 (`task-manager-api` · Python/Flask+SQLAlchemy)
- [ ] Copiar `.claude/skills/refactor-arch/` para o projeto
- [ ] Fase 1: stack detectada (Python/Flask, Task Manager)
- [ ] Fase 2: >=5 findings mesmo parcialmente organizado, com file:line
- [ ] GATE Fase 2->3: confirmação
- [ ] Fase 3: `src/` MVC (services/utils viram camada real)
- [ ] Validação: seed + boot + endpoints
- [ ] `reports/audit-project-3.md` salvo
- [ ] Commit na `main` + push
- [ ] CHECK-IN com usuário

## M4 — Finalização
- [ ] README.md seções A/B/C/D preenchidas
- [ ] Checklist de aceite marcado (3/3 projetos)
- [ ] Commit final na `main` + push

---

## Log de progresso
- Exploração inicial dos 3 projetos concluída (stacks, domínios e anti-patterns mapeados).
- M0 concluído: `reports/` e `LISTA.md` criados.
