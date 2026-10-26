# 🛡️ Projeto Final — Missão Clube Aurora | DevSecOps (Turma 1746)

> **Repositório Oficial do Projeto no GitHub:**  
> 👉 [https://github.com/estelamell0/devsecops-1746-projeto-final](https://github.com/estelamell0/devsecops-1746-projeto-final)

Bem-vindo(a) à atividade de entrega do **Projeto Final de DevSecOps**!

Todo o código-fonte da aplicação, os testes automatizados, os fluxos de CI/CD no GitHub Actions e os materiais de apoio estão centralizados no repositório oficial acima. Neste projeto prático e **estritamente individual**, você atuará como especialista em DevSecOps para diagnosticar, auditar e remediar vulnerabilidades críticas em um ambiente que simula uma operação corporativa em rápida expansão.

Leia atentamente as orientações abaixo, escolha a sua trilha de especialização e realize a entrega do seu relatório preenchido diretamente nesta atividade do LMS.

---

## 1. 🏢 Contexto Corporativo & Escopo da Auditoria (Clube Aurora)

- **A Plataforma:** O **Clube Aurora** é uma plataforma corporativa voltada à gestão de clientes de altíssima renda e agendamento de experiências exclusivas (concierge VIP, fretamento de jatos executivos, leilões de arte e eventos fechados).
- **Stack Tecnológica Real:** 
  - Linguagem e Framework: Python 3.11 com Flask 3
  - Banco de Dados: SQLite 3 persistido em arquivo
  - Servidor de Aplicação: Gunicorn (WSGI)
  - Conteinerização & Orquestração: Docker (Multi-stage build) e Docker Compose
  - Testes & Automação: Pytest e GitHub Actions (esteira com 5 jobs e Quality Gates)
- **O Cenário de Negócio:** Em razão da expansão comercial acelerada, a liderança priorizou a entrega rápida de funcionalidades, acumulando dívida técnica e **7 vetores críticos de vulnerabilidade** que abrangem código-fonte, dependências, credenciais, contêineres e orquestração.
- **O Seu Papel:** Atuar como Especialista em DevSecOps responsável pelo diagnóstico técnico, modelagem de ameaças, mitigação de riscos e garantia dos Quality Gates na esteira de deploy.

---

## 2. 🎯 Escolha da Trilha de Especialização (Critérios de Elegibilidade)

O projeto é **individual**. Para atender aos diferentes objetivos de carreira, você deve escolher **apenas UMA** das 3 trilhas abaixo. Todas trabalham sobre o mesmo caso do Clube Aurora e possuem idêntico rigor e peso avaliativo (**100 pontos**):

| Trilha | Foco de Competência | Escopo de Execução |
|---|---|---|
| **Trilha 1: Teórica Guiada (TG)** | Governança, GRC, Auditoria & Gestão de Riscos | **100% no material didático (sem código nem Docker).**<br>Modelagem STRIDE, matriz de riscos 5x5 e plano de ação executivo com base nos relatórios reais de scanners já pré-gerados em `docs/trilha_1/evidencias/`. |
| **Trilha 2: Híbrida / Mista (TM)** | Engenharia de Software & Modelagem de Ameaças | **Prática no Código:** Criar um fork, corrigir as falhas F1, F2 e F4 (ou F1–F3) e validar localmente via `python scripts/selfcheck.py --nivel 2`.<br>**Análise Teórica:** Modelagem de ameaças STRIDE e mitigação conceitual de F3, F5, F6 e F7 em relatório. |
| **Trilha 3: Engenharia Técnica Completa (TC)** | DevSecOps Full-Cycle, Hardening & CI/CD | **Resolução Integral no Código:** Criar um fork, corrigir todas as 7 falhas (F1 a F7), deixar os 5 jobs do GitHub Actions verdes e validar via `python scripts/selfcheck.py --nivel 3`. |

---

## 3. 🛡️ Catálogo Técnico das 7 Falhas Mapeadas (Matriz CWE / OWASP)

Detalhamento formal das vulnerabilidades presentes no repositório `aurora/`:

| ID | Classificação Técnica | Localização no Repositório | Ferramenta de Detecção |
|---|---|---|---|
| **F1** | Hardcoded Credentials & Repository Leakage (CWE-798 / Crítica) | `aurora/.env` & `.gitignore` | Gitleaks / Secret Scan |
| **F2** | Vulnerable & Outdated Components (SCA / CVEs Críticos) | `aurora/requirements.txt` | Trivy FS (SCA) |
| **F3** | SQL Injection via String Formatting (CWE-89 / Alta) | `aurora/app/db.py` (`search_clients`) | Semgrep SAST (`p/owasp-top-ten`) |
| **F4** | Insecure Container Configuration & Non-Root Violation (Média) | `aurora/Dockerfile` | Hadolint & Trivy Image |
| **F5** | Missing Defensive HTTP Security Headers (Média) | `aurora/app/main.py` & `app/__init__.py` | OWASP ZAP Baseline (DAST) |
| **F6** | Broken Access Control & Privilege Escalation (CWE-284 / Alta) | `aurora/app/db.py` & `app/main.py` | Revisão RBAC / Pytest |
| **F7** | Overprivileged Container Orchestration (IaC Permissiva / Alta) | `aurora/docker-compose.yml` | Inspeção IaC / CIS Benchmark |

---

## 4. 📤 Instruções Exatas de Submissão no LMS (O que anexar)

Instruções para envio na caixa de entrega desta atividade:

### 🔹 Envio para Trilha 1 (TG):
- **Upload do Arquivo:** Anexar o relatório preenchido `RELATORIO_FINAL_TRILHA_1.pdf` (ou `.docx`), estruturado a partir do modelo [`docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx) (ou `docs/TEMPLATE_TG.md`).
- *Nota:* Não é necessário criar fork nem rodar pipeline. Todas as evidências técnicas já estão pré-geradas na pasta `docs/trilha_1/evidencias/`.

### 🔹 Envio para Trilha 2 (TM):
- **Upload do Arquivo:** Anexar o relatório analítico preenchido `RELATORIO_TRILHA_2.pdf` (ou `.docx`), baseado em [`docs/docx/TEMPLATE_TM.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/docx/TEMPLATE_TM.docx) (ou `docs/TEMPLATE_TM.md`).
- **Link do Repositório/PR:** Informe o link público do seu fork no GitHub e do Pull Request no **cabeçalho do documento**. *(Caso deseje incluir os prints das checagens locais do `selfcheck.py --nivel 2` ou dos steps do pipeline, você pode inseri-los ao final do próprio relatório `TEMPLATE_TM` ou anexar o `TEMPLATE_EVIDENCIAS`)*.

### 🔹 Envio para Trilha 3 (TC):
- **Campo de Texto do LMS:** Inserir o link público do seu fork no GitHub com a aba Actions aberta demonstrando a esteira completa verde.
- **Upload do Arquivo:** Anexar o dossiê de evidências preenchido `EVIDENCIAS_PIPELINE.pdf` (ou `.docx`), baseado em [`docs/docx/TEMPLATE_EVIDENCIAS.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/docx/TEMPLATE_EVIDENCIAS.docx) (ou `docs/TEMPLATE_EVIDENCIAS.md`), contendo no cabeçalho o link público do repositório/fork e do PR principal com todos os Quality Gates verdes.

> ⚠️ **Atenção (Trilhas 2 e 3):** Certifique-se de que o seu repositório no GitHub seja **público** (ou que a professora `estelamell0` seja adicionada como colaboradora) para viabilizar a auditoria do código e a conferência dos logs de execução.

---

## 5. 📊 Critérios de Avaliação e Ponderação da Rubrica (100 Pontos)

Resumo executivo da matriz de pontuação extraída de `aurora/docs/RUBRICA.md`:

- **Trilha 1 (Teórica Guiada — TG):**
  - Modelagem de Ameaças STRIDE: **30 pontos**
  - Matriz de Riscos 5x5 & Impacto LGPD/Negócio: **30 pontos**
  - Plano de Ação Executivo e Mitigações: **40 pontos**
- **Trilha 2 (Híbrida / Mista — TM):**
  - Correção prática no código e validação local/CI: **50 pontos**
  - Análise teórica e remediação conceitual de F3, F5–F7: **50 pontos**
- **Trilha 3 (Engenharia Técnica Completa — TC):**
  - Correção integral das 7 falhas no código e IaC: **40 pontos**
  - Pipeline CI/CD com 5 Quality Gates verdes: **40 pontos**
  - Dossiê de evidências e higiene de Git/Commits: **20 pontos**

---

## 6. 🧰 Guia de Acesso aos Recursos no Repositório aurora/

Todos os materiais de apoio estão organizados na pasta `docs/` do repositório oficial:

- **Central da Trilha 1:** Hub consolidado em [`docs/trilha_1/`](https://github.com/estelamell0/devsecops-1746-projeto-final/tree/main/docs/trilha_1) (Manual Completo com índice, Dicionário de Segurança e relatórios técnicos pré-gerados prontos para análise).
- **Autoavaliação para Trilhas 2 e 3:** Como rodar o validador no terminal antes da entrega:
  ```bash
  # Para alunos da Trilha 2 (valida correções de F1, F2 e F4):
  python scripts/selfcheck.py --nivel 2

  # Para alunos da Trilha 3 (valida todas as 7 falhas F1 a F7):
  python scripts/selfcheck.py --nivel 3
  ```
- **Templates Editáveis para Download:**
  - **Trilha 1:** [`docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx) (ou `docs/TEMPLATE_TG.md`)
  - **Trilha 2:** [`docs/docx/TEMPLATE_TM.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/docx/TEMPLATE_TM.docx) (ou `docs/TEMPLATE_TM.md`)
  - **Trilha 3:** [`docs/docx/TEMPLATE_EVIDENCIAS.docx`](https://github.com/estelamell0/devsecops-1746-projeto-final/blob/main/docs/docx/TEMPLATE_EVIDENCIAS.docx) (ou `docs/TEMPLATE_EVIDENCIAS.md`)
