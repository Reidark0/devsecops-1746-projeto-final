# Relatório de Evidências Técnicas - Clube Aurora

**Nome do Aluno(a):** [Seu Nome Aqui]  
**Turma:** DevSecOps 1746  
**Trilha Escolhida:** [ ] Trilha 2 (Mista) | [ ] Trilha 3 (Técnica)  
**Link do Repositório / Fork no GitHub:** `https://github.com/seu-usuario/seu-repo` *(Caso o repositório seja privado, certifique-se de adicionar a professora como colaboradora para avaliação)*  
**Link do Pull Request Principal:** `https://github.com/seu-usuario/seu-repo/pull/1`

---

## 1. Evidência do Pipeline Inicial (Antes das Correções)

Cole aqui o print ou log demonstrando o pipeline falhando no estado inicial:

- **Screenshot da Aba Actions (Pipeline com steps vermelhos):**
  *(Cole a imagem aqui ou link do commit inicial)*
- **Principais falhas apontadas pelas ferramentas:**
  - Hadolint: [...]
  - Trivy FS: [...]
  - Semgrep: [...]

---

## 2. Resumo das Correções Implementadas

Descreva brevemente como você corrigiu cada achado sob seu escopo técnico:

| Achado | Arquivo Modificado | Resumo da Alteração Realizada |
|---|---|---|
| **F1: Segredos** | `.gitignore` / `.env` | |
| **F2: SCA** | `requirements.txt` | |
| **F3: SAST** *(Trilha 3)* | `app/db.py` | |
| **F4: Hardening** | `Dockerfile` | |
| **F5: DAST** *(Trilha 3)* | `app/main.py` e `app/__init__.py` | |
| **F6: Menor Privilégio** *(Trilha 3)* | `app/db.py` / `app/main.py` | |
| **F7: IaC** *(Trilha 3)* | `docker-compose.yml` | |

---

## 3. Evidência do Pipeline Final (Após as Correções)

Cole aqui a comprovação de que o pipeline foi executado com sucesso:

- **Screenshot da Aba Actions (Todos os steps com check verde):**
- **Link direto para a execução bem-sucedida do Actions:** `https://github.com/.../actions/runs/...`
- **Proteção da Branch Main:**
  *(Print da configuração de Branch Protection Rules no GitHub exigindo status checks antes do merge)*

---

## 4. (Opcional - Trilha 3) Justificativa de Aceitação de Risco (`.trivyignore`)
Se houver alguma vulnerabilidade de severidade MEDIUM mantida:
- **CVE ou ID:** [...]
- **Justificativa de negócio e prazo para correção:** [...]
