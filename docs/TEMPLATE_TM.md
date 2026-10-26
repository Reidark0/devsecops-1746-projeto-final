# Relatório Técnico-Analítico — Clube Aurora (Trilha 2 — Mista)

**Nome do Aluno(a):** [Seu Nome Aqui]  
**Turma:** DevSecOps 1746  
**Data:** [Data de Entrega]  
**Link do Repositório / Fork no GitHub:** `https://github.com/seu-usuario/seu-repo` *(Caso o repositório seja privado, certifique-se de adicionar a professora como colaboradora para avaliação)*  
**Link do Pull Request Principal:** `https://github.com/seu-usuario/seu-repo/pull/1`

---

## 1. Resumo das Correções Práticas de Engenharia (Código e Contêiner)

Descreva brevemente como você corrigiu as falhas práticas do seu escopo (F1, F2 e F4):

| Achado Prático | Arquivo Modificado | Resumo da Alteração Implementada |
|---|---|---|
| **F1: Segredos Hardcoded** | `.gitignore` e `.env` | *(Ex: Removido .env do versionamento git, adicionado ao .gitignore e criado .env.example seguro)* |
| **F2: SCA (Dependências)** | `requirements.txt` | *(Ex: Atualizadas versões de Flask, Werkzeug e Gunicorn para mitigar CVEs conhecidas)* |
| **F4: Hardening de Imagem** | `Dockerfile` | *(Ex: Imagem base python:3.11-slim, usuário não-root, sem cache e HEALTHCHECK configurado)* |

### Evidência de Validação Prática:
Cole aqui a comprovação de validação da sua entrega prática (print do terminal com o `python scripts/selfcheck.py --nivel 2` aprovado **OU** print dos steps correspondentes verdes no GitHub Actions):

> *(Cole a imagem da execução do selfcheck ou dos steps do Actions aqui)*

---

## 2. Análise de Ameaças (STRIDE & Tríade CIA)

Preencha a matriz de análise para os 4 achados conceituais da Trilha 2 (Mista):

| Achado | Componente / Arquivo | Categoria STRIDE | Pilar CIA Afetado | Impacto no Negócio do Clube Aurora |
|---|---|---|---|---|
| **F3: SQL Injection** | `app/db.py` (`search_clients`) | | | |
| **F5: Ausência de Headers HTTP** | `app/main.py` e `app/__init__.py` | | | |
| **F6: Quebra de Menor Privilégio** | `app/db.py` / `app/main.py` | | | |
| **F7: IaC Permissiva (Docker Compose)** | `docker-compose.yml` | | | |

---

## 3. Decisão de Arquitetura & Governança (F6)

O Tio Armando solicitou que a nova gerente de atendimento, Carla, receba privilégios de **Admin geral** do sistema.
1. Analise o pedido sob a ótica de **Segregação de Funções (SoD)** e **Menor Privilégio**.
2. Qual modelo de controle de acesso (RBAC) você recomenda para o Clube Aurora (papéis, permissões por rota)?
3. Como você responderia ao Tio Armando para recusar o admin total e propor a solução adequada?

---

## 4. Observabilidade e Detecção de Intrusão

Caso uma conta de funcionário seja comprometida ou ocorram tentativas de força bruta na API:
1. Quais eventos mínimos devem ser registrados no log de auditoria (`audit_log`)?
2. Como a equipe de operações saberia que um ataque de SQL Injection ou login malicioso está ocorrendo em tempo hábil?
