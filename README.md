# Clube Aurora - Sistema de Gestão de Concierge VIP

Bem-vindo ao repositório do **Clube Aurora**. Este é o projeto base utilizado na avaliação prática e estudos de caso da disciplina de **DevSecOps (Turma 1746)**.

---

## 📚 Central de Instruções e Entrega do Aluno

> 🎯 **Você é aluno(a) da Trilha 1 (Teórica Guiada)?**  
> Acesse a pasta exclusiva **[`docs/trilha_1/`](./docs/trilha_1/)**!  
> Lá você encontra tudo o que precisa reunido em um só lugar, sem complicações:  
> - 📄 **[MANUAL_COMPLETO_TRILHA_1.pdf](./docs/trilha_1/MANUAL_COMPLETO_TRILHA_1.pdf)**: Manual único consolidado com índice clicável (enunciado, guia passo a passo, casos práticos, rubrica e checklist);  
> - 📖 **[GLOSSARIO_DEVSECOPS_DETALHADO.pdf](./docs/trilha_1/GLOSSARIO_DEVSECOPS_DETALHADO.pdf)**: Dicionário completo de segurança com definições aprofundadas de todos os conceitos da disciplina;  
> - 📝 **[TEMPLATE_ENTREGA_TRILHA_1.docx](./docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx)**: Arquivo Word editável pronto para preenchimento;  
> - 📁 **[evidencias/](./docs/trilha_1/evidencias/)**: Relatórios técnicos dos scanners prontos para análise.  
> *(Você não precisa rodar Docker nem alterar códigos!)*

### 🤔 Ainda não escolheu sua trilha?
Todas as trilhas trabalham com o mesmo caso do **Clube Aurora** e possuem peso acadêmico idêntico. A diferença está no seu foco de aprendizado:
- **Quer focar em Gestão, Riscos e Auditoria de Segurança?** $\rightarrow$ A **Trilha 1** foi feita para você analisar relatórios reais, avaliar dilemas de negócio e tomar decisões executivas sem precisar configurar Docker ou alterar código.
- **Quer unir Modelagem de Ameaças com correções pontuais de vulnerabilidades?** $\rightarrow$ A **Trilha 2** equilibra o raciocínio STRIDE com a resolução das falhas no código.
- **Quer mergulhar de cabeça em CI/CD, automação de testes e hardening de infraestrutura?** $\rightarrow$ A **Trilha 3** desafia você a deixar o pipeline 100% verde direto no terminal e no GitHub Actions.

💡 **Dica de Ouro:** Não tenha medo de ser curioso(a)! Você pode começar explorando o material da **Trilha 1** para entender a história e o contexto da aplicação e, se a vontade bater, abrir o código e migrar para as Trilhas 2 ou 3 a qualquer momento.

---

Seja bem-vindo(a) ao projeto prático do **Clube Aurora**! Todos os arquivos de instruções, guias de sobrevivência por trilha e templates de entrega estão disponíveis na pasta [`docs/`](./docs/):

| Documento | Leitura Online (MD) | Download PDF | Arquivo de Entrega (Preenchível) | Trilha Indicada |
|---|:---:|:---:|:---:|---|
| **Manual Completo Trilha 1** | [Visualizar](./docs/MANUAL_COMPLETO_TRILHA_1.md) | **[Baixar PDF](./docs/trilha_1/MANUAL_COMPLETO_TRILHA_1.pdf)** | — | **Trilha 1 (Hub Completo)** |
| **Glossário Detalhado** | [Visualizar](./docs/GLOSSARIO_DEVSECOPS_DETALHADO.md) | **[Baixar PDF](./docs/trilha_1/GLOSSARIO_DEVSECOPS_DETALHADO.pdf)** | — | Todas / Trilha 1 |
| **Enunciado & Contexto** | [Visualizar](./docs/ENUNCIADO.md) | [Baixar PDF](./docs/pdf/ENUNCIADO.pdf) | — | Todas |
| **Critérios e Rubrica** | [Visualizar](./docs/RUBRICA.md) | [Baixar PDF](./docs/pdf/RUBRICA.pdf) | — | Todas |
| **Checklist de Entrega** | [Visualizar](./docs/CHECKLIST_ENTREGA.md) | [Baixar PDF](./docs/pdf/CHECKLIST_ENTREGA.pdf) | — | Todas |
| **Guia Trilha 1 (Teórico)** | [Visualizar](./docs/GUIA_TRILHA_1_TEORICA.md) | [Baixar PDF](./docs/pdf/GUIA_TRILHA_1_TEORICA.pdf) | — | **Trilha 1** |
| **Guia Trilha 2 (Misto)** | [Visualizar](./docs/GUIA_TRILHA_2_MISTA.md) | [Baixar PDF](./docs/pdf/GUIA_TRILHA_2_MISTA.pdf) | — | Trilha 2 |
| **Guia Trilha 3 (Técnico)** | [Visualizar](./docs/GUIA_TRILHA_3_TECNICA.md) | [Baixar PDF](./docs/pdf/GUIA_TRILHA_3_TECNICA.pdf) | — | Trilha 3 |
| **Plano de Testes CLI** | [Visualizar](./docs/PLANO_DE_TESTES_DEBUGGING.md) | [Baixar PDF](./docs/pdf/PLANO_DE_TESTES_DEBUGGING.pdf) | — | Trilhas 2 e 3 |
| **Como Ler Relatórios** | [Visualizar](./docs/COMO_LER_OS_RELATORIOS.md) | [Baixar PDF](./docs/pdf/COMO_LER_OS_RELATORIOS.pdf) | — | Todas |
| **Glossário DevSecOps** | [Visualizar](./docs/GLOSSARIO.md) | [Baixar PDF](./docs/pdf/GLOSSARIO.pdf) | — | Todas |
| **Relatório Trilha 1** | [Visualizar](./docs/TEMPLATE_TG.md) | — | **[Baixar Word (.docx)](./docs/trilha_1/TEMPLATE_ENTREGA_TRILHA_1.docx)** | **Trilha 1** |
| **Relatório Trilha 2** | [Visualizar](./docs/TEMPLATE_TM.md) | — | **[Baixar Word (.docx)](./docs/docx/TEMPLATE_TM.docx)** | **Trilha 2** |
| **Evidências Trilha 2/3** | [Visualizar](./docs/TEMPLATE_EVIDENCIAS.md) | — | **[Baixar Word (.docx)](./docs/docx/TEMPLATE_EVIDENCIAS.docx)** | **Trilhas 2 e 3** |

> 💡 **Dica de Início Rápido:**
> - Se você está na **Trilha 1 (Teórica Guiada)**: Vá direto para a pasta [`docs/trilha_1/`](./docs/trilha_1/)! Baixe o **`MANUAL_COMPLETO_TRILHA_1.pdf`** e o arquivo Word **`TEMPLATE_ENTREGA_TRILHA_1.docx`**, consulte as evidências em [`docs/trilha_1/evidencias/`](./docs/trilha_1/evidencias/) e o **`GLOSSARIO_DEVSECOPS_DETALHADO.pdf`**. Você **não** precisa rodar o Docker nem alterar código!
> - Se você está na **Trilha 2 ou 3**: Siga as instruções de execução local e use o **Plano de Testes CLI** e o script de autoavaliação (`selfcheck.py`) para validar suas alterações passo a passo.

---

## 📖 Sobre a Aplicação
O Clube Aurora é uma plataforma interna desenvolvida para gerenciar clientes VIP (alta renda) e agendar experiências personalizadas (viagens em jatos privados, compra em leilões de arte e camarotes exclusivos).

### Stack Tecnológica
- **Linguagem:** Python 3.11
- **Framework Web:** Flask 3
- **Banco de Dados:** SQLite 3 (persistido em arquivo)
- **Servidor WSGI:** Gunicorn
- **Containers:** Docker & Docker Compose
- **Testes Automatizados:** Pytest

---

## 🚀 Como Executar Localmente

### Opção 1: Via Docker Compose (Recomendado)
```bash
docker compose up --build
```
A API estará acessível em: `http://localhost:8080`

Para testar a integridade da aplicação:
```bash
curl http://localhost:8080/health
# Resposta esperada: {"status":"ok"}
```

### Opção 2: Executando Diretamente no Host (com Python)
```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou no Windows: .venv\Scripts\Activate.ps1

# 2. Instale as dependências
pip install -r requirements-dev.txt

# 3. Inicialize o banco de dados de teste/seed
flask --app app init-db

# 4. Inicie o servidor de desenvolvimento
flask --app app run --port 8080
```

---

## 🧪 Como Executar os Testes Unitários

Para garantir que a aplicação está íntegra:
```bash
pytest -v
```

---

## 🔍 Autoavaliação Local (Self-Check)

Antes de abrir um Pull Request ou disparar o workflow no GitHub Actions, você pode validar localmente suas correções com o script de autoavaliação (apenas biblioteca padrão do Python):

```bash
# Se você está cursando a Trilha Nível 2 (Mista - F1, F2 e F4):
python scripts/selfcheck.py --nivel 2

# Se você está cursando a Trilha Nível 3 (Técnica - F1 a F7):
python scripts/selfcheck.py --nivel 3
```

O script retornará exit code `0` apenas se todas as falhas selecionadas estiverem devidamente sanadas, exibindo dicas progressivas caso algum item precise de ajuste.

---

## 🛡️ Esteira de DevSecOps (GitHub Actions)
Este repositório contém uma esteira automatizada configurada em `.github/workflows/devsecops.yml`.

Toda vez que você enviar alterações via `git push` ou abrir um `Pull Request` para a branch `main`, os seguintes scans serão executados:
1. **Linting de Dockerfile:** Hadolint
2. **SCA & Secrets:** Trivy Filesystem
3. **SAST:** Semgrep (regras OWASP Top 10)
4. **Scan de Container:** Trivy Image
5. **Geração de SBOM:** CycloneDX
6. **DAST:** OWASP ZAP Baseline Scan

> 📌 **Importante:** Seu objetivo prático é analisar os relatórios das ferramentas, corrigir as vulnerabilidades identificadas e fazer a esteira ficar verde (`passed`)!
>
> 💡 **Visibilidade (Público ou Privado):**  
> Este repositório suporta uma abordagem híbrida:
> - **Público (Recomendado):** Permite visualizar as vulnerabilidades diretamente na interface gráfica da aba **Security** (Code Scanning Alerts) do GitHub.
> - **Privado:** Totalmente suportado! Se você preferir manter seu repositório privado, o pipeline rodará sem quebrar; você poderá consultar os relatórios formatados em tabelas nos logs da aba **Actions** e baixar os arquivos completos na seção **Artifacts**.
