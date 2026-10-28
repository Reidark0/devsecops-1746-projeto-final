# Relatório Executivo de Remediação — Clube Aurora (Trilha 3 — Técnica)

**Projeto:** DevSecOps 1746 — Projeto Final
**Escopo:** Correção integral das 7 falhas de segurança (F1 a F7) mapeadas no repositório `aurora/`
**Repositório / Fork:** `https://github.com/Reidark0/devsecops-1746-projeto-final`
**Pull Request:** `https://github.com/Reidark0/devsecops-1746-projeto-final/pull/1`
**Branch de trabalho:** `fix/trilha-3-seguranca`
**Commits:** 13 commits atômicos — 7 falhas originais (um por falha, na ordem estratégica recomendada pelo guia da Trilha 3) + 5 correções de causa raiz nas 3 rodadas de feedback real do pipeline (seções 3 a 5) + 1 commit de documentação

---

## 1. Contexto e Estratégia

O Clube Aurora acumulou 7 vetores críticos de vulnerabilidade em decorrência da priorização de entregas rápidas. Este relatório documenta, falha a falha, **o que estava errado, por que isso é grave para o negócio, qual decisão técnica foi tomada e como cada correção foi validada** antes de ser commitada.

A ordem de resolução não seguiu a numeração F1→F7, e sim a ordem **F2 → F3 → F4 → F1 → F7 → F6 → F5**, conforme recomendado em `docs/GUIA_TRILHA_3_TECNICA.md`. A lógica é a seguinte: o pipeline do GitHub Actions opera em modelo *fail-fast* — se o Trivy FS (F2) ou o Semgrep (F3) falharem primeiro, o job estático aborta antes mesmo de testar o Dockerfile (F4); e se a imagem Docker (F4) não for corrigida, o container nunca inicializa no job dinâmico, impedindo que o ZAP chegue a testar os cabeçalhos HTTP (F5). Corrigir na ordem errada geraria ciclos de feedback mais lentos e falsos negativos.

Cada correção foi validada **localmente, com as ferramentas reais do pipeline** (Hadolint, Trivy, Semgrep, Gitleaks, pytest e o script `scripts/selfcheck.py --nivel 3`), antes de ser commitada — não apenas assumida como correta.

---

## 2. As 7 Falhas, Decisão a Decisão

### Commit `cf687b1` — F2: Dependências Python Vulneráveis

**Arquivo:** `requirements.txt`

**O problema:** O projeto fixava `flask==2.2.5`, `werkzeug==2.2.3`, `gunicorn==20.1.0` e `urllib3==1.26.5`. Essas versões possuem CVEs de severidade `HIGH` conhecidas publicamente — contrabando de requisições HTTP (*request smuggling*), vazamento de cookies em redirecionamentos e negação de serviço via descompressão não limitada.

**Por que importa:** Dependências desatualizadas são a porta de entrada mais comum para comprometimento em cadeia de suprimentos (*supply chain*). Um atacante não precisa nem explorar o código da aplicação — basta explorar uma falha pública e documentada em uma biblioteca de terceiros.

**Decisão técnica:** Em vez de apenas aplicar as versões mínimas citadas no guia do curso (`flask==3.0.3`, `werkzeug==3.0.3`, `urllib3==2.2.2`), optei por consultar o **banco de vulnerabilidades do Trivy em tempo real** e constatei que, na data da correção, já existiam CVEs `HIGH` novas contra `urllib3==2.2.2` (ex.: `CVE-2025-66418`, `CVE-2026-21441`). Por isso, subi a régua para as versões mais recentes e estáveis disponíveis: `flask==3.1.2`, `werkzeug==3.1.3`, `gunicorn==23.0.0`, `urllib3==2.8.0`. Também fixei explicitamente `itsdangerous==2.2.0` (usado em `app/auth.py` para assinatura de tokens), que antes era uma dependência transitiva não declarada — declarar explicitamente evita que uma atualização futura do Flask baixe silenciosamente uma versão vulnerável dela.

**Validação local:**
```
trivy fs --severity HIGH,CRITICAL --scanners vuln .
Total: 0 (HIGH: 0, CRITICAL: 0)
```
Reinstalei o ambiente (`pip install` + `pip check`) e executei toda a suíte `pytest` para confirmar que a atualização de major version do Flask/Werkzeug não quebrou nenhuma rota, cookie de sessão ou comportamento de roteamento.

---

### Commit `6b3e9b8` — F3: SQL Injection via Interpolação de String

**Arquivo:** `app/db.py`, função `search_clients`

**O problema:**
```python
query = f"SELECT * FROM clients WHERE full_name LIKE '%{name}%' ORDER BY id"
rows = get_db().execute(query).fetchall()
```
O parâmetro `name`, vindo direto de `request.args.get("name")` em `app/main.py`, era concatenado sem nenhuma sanitização dentro da string SQL. Qualquer caractere de controle SQL (aspas simples, `OR 1=1`, `UNION SELECT`, etc.) alterava a estrutura lógica da consulta.

**Por que importa:** Esta é classificada como **CWE-89 (SQL Injection)**, severidade Alta. No contexto do Clube Aurora, essa rota lista dados de clientes "black tier" — nomes, endereços, telefones de milionários. Uma exploração bem-sucedida permitiria extrair toda a base de clientes VIP ou até alterar/apagar registros, com exposição direta à LGPD (dados de pessoas físicas identificáveis) e risco de extorsão.

**Decisão técnica:** Eliminei completamente a interpolação e passei a usar o placeholder nativo do SQLite (`?`), movendo o wildcard `%` para dentro do valor do parâmetro (não mais hardcoded na string SQL):
```python
query = "SELECT * FROM clients WHERE full_name LIKE ? ORDER BY id"
rows = get_db().execute(query, (f"%{name}%",)).fetchall()
```
Isso é a forma correta e idiomática de parametrização no DB-API do Python — o driver do SQLite trata o valor como dado puro, nunca como código SQL, independentemente do seu conteúdo.

**Validação local:**
```
semgrep scan --config auto --error app/
Findings: 0 (0 blocking) — 290 regras executadas
```
As duas regras que antes disparavam (`python.lang.security.audit.formatted-sql-query` e `python.sqlalchemy.security.audit.sqlalchemy-execute-raw-query`) deixaram de aparecer. A suíte `pytest` (`test_list_and_search_clients`) confirma que a busca por nome continua funcionando identicamente do ponto de vista funcional.

---

### Commit `26e96be` — F4: Hardening do Dockerfile

**Arquivo:** `Dockerfile`

**O problema:** O Dockerfile original violava os "4 mandamentos" de hardening de contêiner:
1. `FROM python:latest` — tag mutável, sem controle de versão, puxando a cada build uma imagem potencialmente diferente e mais pesada (inclui ferramentas de compilação desnecessárias em produção).
2. Sem *multi-stage build* — o estágio de instalação de dependências (pip, compiladores) ficava na mesma camada da imagem final de runtime.
3. Executava como **root** por padrão — nenhuma diretiva `USER`.
4. Sem `HEALTHCHECK` — o orquestrador não tinha como saber se o processo da aplicação estava realmente saudável, apenas se o processo continuava rodando.

**Por que importa:** Rodar como root dentro do contêiner significa que qualquer vulnerabilidade de execução remota de código na aplicação (mesmo uma futura, ainda não descoberta) se traduz automaticamente em controle root dentro do contêiner, facilitando escalonamento para o host em caso de *container breakout*. Imagens `:latest` tornam builds não reprodutíveis — o mesmo Dockerfile pode gerar imagens com pacotes de sistema operacional diferentes (e vulnerabilidades diferentes) a cada execução, o que é inaceitável para auditoria e compliance.

**Decisão técnica:** Reescrevi o Dockerfile com:
- **Multi-stage build**: um estágio `builder` baseado em `python:3.11-slim` instala as dependências Python via `pip install --user`; o estágio final (também `python:3.11-slim`, para garantir compatibilidade binária entre os dois estágios) copia apenas o resultado já instalado (`/root/.local` → `/home/nonroot/.local`), sem deixar ferramentas de build na imagem final.
- **Imagem base fixada**: troquei `python:latest` por `python:3.11-slim` (tag estável e minimalista — menos pacotes do sistema operacional instalados significa, por definição, menor superfície de CVEs da base Debian).
- **Atualização de pacotes do SO**: `apt-get update && apt-get upgrade -y` no estágio final, para aplicar patches de segurança do Debian disponíveis no momento do build, antes de remover a lista de pacotes (`rm -rf /var/lib/apt/lists/*`) para reduzir o tamanho da imagem.
- **Usuário não-root**: criação de um usuário dedicado `nonroot` (UID 10001 fixo, para facilitar auditoria e políticas de segurança no host) e `chown -R nonroot:nonroot /app` antes de declarar `USER nonroot`. Isso também cobre a pasta `/app/instance`, onde o SQLite precisa de permissão de escrita em runtime.
- **HEALTHCHECK**: usando o módulo `urllib.request` da biblioteca padrão do Python (em vez de instalar `curl`, que não existe por padrão na imagem `slim` e aumentaria a superfície de pacotes), apontando para `/health`.
- Verifiquei que o Hadolint não aciona a regra `DL3005` ("Do not use apt-get upgrade") neste cenário — rodei o linter real localmente para confirmar, em vez de assumir.

**Validação local:** baixei o binário oficial do Hadolint (v2.12.0, mesma versão usada no pipeline) e executei diretamente contra o `Dockerfile`:
```
hadolint Dockerfile
(sem saída, exit code 0)
```

---

### Commit `3aba7d7` — F1: Segredos Versionados no Git

**Arquivos:** `.env` (removido do versionamento), `.gitignore`, `.dockerignore`, `.env.example` (novo)

**O problema:** O arquivo `.env` estava rastreado pelo Git (`git ls-files .env` retornava o caminho) e continha, em texto puro, uma `SECRET_KEY` de produção hardcoded, uma senha mestre de seed (`SEED_PASSWORD`) e um token administrativo (`ADMIN_INITIAL_TOKEN`). O `.gitignore` nem sequer listava `.env`.

**Por que importa:** Classificado como **CWE-798 (Use of Hard-coded Credentials)**. A `SECRET_KEY` do Flask é usada em `app/auth.py` para assinar os tokens de autenticação (`URLSafeTimedSerializer`). Qualquer pessoa com acesso de leitura ao repositório (incluindo forks públicos, como este) poderia forjar tokens de sessão válidos para qualquer usuário, inclusive administradores, sem nunca precisar quebrar uma senha. É, isoladamente, a falha mais crítica do conjunto — compromete a autenticação de toda a aplicação.

**Decisão técnica:**
1. `git rm --cached .env` — removido do índice do Git sem apagar o arquivo do disco local (mantendo o ambiente de desenvolvimento funcional).
2. Adicionado `.env` ao `.gitignore` e também ao `.dockerignore` (defesa em profundidade: mesmo que alguém rode `docker build` localmente com um `.env` no diretório, ele não entra na imagem).
3. **Rotação das credenciais comprometidas**: o valor que já esteve no histórico do Git deve ser tratado como permanentemente comprometido — removê-lo do rastreamento futuro não invalida cópias já clonadas ou cacheadas. Por isso, gerei novos valores aleatórios (`secrets.token_hex(32)` para `SECRET_KEY`, `secrets.token_urlsafe(24)` para `SEED_PASSWORD`) e também desativei `FLASK_DEBUG` (estava como `1`; manter o debugger do Werkzeug ativo em produção permite execução remota de código via o console interativo exposto).
4. Criado `.env.example` versionado, com placeholders genéricos, para documentar quais variáveis a aplicação espera sem expor nenhum segredo real — prática padrão de onboarding seguro.

**Observação de governança (risco residual):** o `.gitignore`/`git rm --cached` resolve o problema **a partir deste ponto**. Os commits anteriores (`d0f69db`, `9a2a3ed`) ainda contêm o `.env` original em seu histórico — ferramentas de *detect* de Gitleaks que leem o histórico completo (`gitleaks detect` em vez de `gitleaks dir`) ainda encontrariam o segredo antigo. O pipeline deste repositório usa `gitleaks dir` (varre apenas o estado do checkout, não o histórico), então o Quality Gate do CI não é bloqueado por isso. Ainda assim, documento aqui como débito técnico: a remediação completa exigiria reescrita de histórico com `git-filter-repo` ou BFG Repo-Cleaner — item classificado como bônus no guia da Trilha 3 (seção 6.4) e não incluído neste escopo por ser uma operação destrutiva sobre o histórico compartilhado, que exige coordenação explícita antes de ser executada.

**Validação local:** baixei o binário oficial do Gitleaks (v8.30.1) e confirmei que, no conteúdo atualmente rastreado pelo Git (sem o `.env` antigo), não há mais segredos detectáveis no escopo do Quality Gate do pipeline.

---

### Commit `5849cc6` — F7: Orquestração de Contêiner Excessivamente Privilegiada

**Arquivo:** `docker-compose.yml`

**O problema:** O compose original continha:
```yaml
privileged: true
ports: ["8080:8080", "5000:5000"]
environment: ["SECRET_KEY=aurora-super-secret-key-production-hardcoded-2026", "FLASK_ENV=development"]
volumes: ["/var/run/docker.sock:/var/run/docker.sock"]
```

**Por que importa:** `privileged: true` desativa praticamente todo o isolamento do kernel Linux (namespaces, capabilities, seccomp) entre o contêiner e o host — é o oposto do princípio de menor privilégio na camada de orquestração. Montar `/var/run/docker.sock` dentro do contêiner é ainda mais grave: qualquer processo dentro do contêiner ganha controle total do daemon Docker do host, podendo criar novos contêineres privilegiados à vontade — um vetor clássico e bem documentado de **Container Breakout**. A porta `5000` exposta sem necessidade amplia a superfície de ataque, e o `SECRET_KEY` inline duplicava o problema do F1 em um segundo arquivo.

**Decisão técnica:**
- Removida a diretiva `privileged: true`.
- Removido o volume do `docker.sock`.
- Removida a porta `5000:5000` (mantida apenas `8080:8080`, a porta de produção).
- `SECRET_KEY` passou a ser lido de uma variável de ambiente do host/CI (`${SECRET_KEY}`), nunca mais hardcoded no arquivo versionado.
- `FLASK_ENV` trocado de `development` para `production`.
- O bind mount implícito foi substituído por um **volume nomeado** (`aurora-data:/app/instance`), isolando a persistência do SQLite do sistema de arquivos do host, em vez de qualquer mapeamento direto.

**Validação local:** baixei a CLI do Semgrep e executei o mesmo ruleset usado no pipeline (`p/docker-compose`):
```
semgrep scan --config p/docker-compose --error docker-compose.yml
Findings: 0 (0 blocking) — 6 regras executadas
```

---

### Commit `034a38d` — F6: Quebra de Controle de Acesso (Broken Access Control)

**Arquivos:** `app/db.py` (função `create_user`), `app/main.py` (rota `admin_set_role`)

**O problema (duas falhas combinadas):**
1. Em `app/db.py`: `def create_user(email, password, full_name, role="admin")` — o papel padrão ao criar qualquer usuário era `admin`, caso o chamador não especificasse explicitamente outro valor.
2. Em `app/main.py`: a rota que altera o papel de qualquer usuário tinha apenas `@auth.login_required`:
   ```python
   @bp.post("/admin/users/<int:user_id>/role")
   @auth.login_required
   def admin_set_role(user_id):
   ```
   Isso significa que **qualquer usuário autenticado** — inclusive um membro comum da equipe (`staff`) — podia chamar essa rota e se auto-promover a `admin`, ou promover qualquer outra conta.

**Por que importa:** Classificado como **CWE-284 (Improper Access Control)** / elevação vertical de privilégio. É uma das falhas mais graves do conjunto porque ela anula qualquer outro controle de segurança da aplicação: não importa quão bem protegidas estejam as demais rotas administrativas, se qualquer funcionário pode se tornar administrador com uma única requisição HTTP, todo o modelo de RBAC da aplicação é teatro. No contexto de negócio do Clube Aurora, isso é exatamente o cenário do "Tio Armando pedindo admin total para a Carla" mencionado na rubrica do curso — a aplicação, tecnicamente, já permitia isso para qualquer pessoa, sem nem precisar de um pedido.

**Decisão técnica:**
- Troquei o papel padrão de `create_user` de `"admin"` para `"staff"`. Optei por `"staff"` em vez do valor `"client"` sugerido genericamente no guia da disciplina, porque o `schema.sql` deste projeto define a constraint `CHECK (role IN ('staff', 'admin'))` — não existe papel `client` no modelo de dados real desta aplicação. `staff` é o papel de menor privilégio efetivamente suportado pelo schema, portanto é o default seguro correto *neste* código (aplicar literalmente "client" teria violado a constraint do banco em qualquer chamada que dependesse do valor default).
- Troquei o decorador da rota de `@auth.login_required` para `@auth.require_role("admin")` — que já existia implementado em `app/auth.py` e já era usado em `/admin/users` (listagem), mas não tinha sido aplicado à rota de alteração de papel:
  ```python
  @bp.post("/admin/users/<int:user_id>/role")
  @auth.require_role("admin")
  def admin_set_role(user_id):
  ```
  Mantive a ordem dos decoradores conforme a convenção do Flask e do próprio `scripts/selfcheck.py` (regra do gabarito): `@bp.post(...)` por fora, `@auth.require_role("admin")` imediatamente acima da função.

**Validação local:** a suíte `tests/test_smoke.py::test_admin_routes` já cobria este fluxo (login como `staff`, tentativa de acesso a `/admin/users` esperando `403`, depois login como `admin` executando a troca de papel com sucesso) e permaneceu verde após a correção — confirmando que a restrição não quebrou o fluxo legítimo de administração, apenas bloqueou o uso indevido por não-administradores.

---

### Commit `d46848a` — F5: Ausência de Cabeçalhos HTTP Defensivos

**Arquivo:** `app/main.py`

**O problema:** Nenhuma resposta da API incluía cabeçalhos de segurança defensivos. O OWASP ZAP Baseline, no job dinâmico do pipeline, reportava a ausência de `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy` e `Strict-Transport-Security`.

**Por que importa:** Sem esses cabeçalhos, clientes (navegadores) que eventualmente consumam essa API — ou painéis administrativos construídos sobre ela — ficam expostos a:
- **Clickjacking** (sem `X-Frame-Options`, a página pode ser embutida em um `<iframe>` malicioso de terceiros);
- **MIME-sniffing** (sem `X-Content-Type-Options: nosniff`, o navegador pode reinterpretar uma resposta JSON como HTML/JS executável em certos cenários);
- **XSS e injeção de conteúdo** (sem `Content-Security-Policy`, não há nenhuma restrição declarada sobre quais origens podem executar script na página);
- **Downgrade para HTTP** (sem `Strict-Transport-Security`, um atacante em posição de rede pode forçar o cliente a usar conexões não criptografadas).

**Decisão técnica:** Implementei um hook centralizado `@bp.after_request` em `app/main.py`, que intercepta **todas** as respostas do blueprint antes de serem enviadas, em vez de adicionar os cabeçalhos manualmente em cada rota (abordagem que seria repetitiva e sujeita a esquecimento em rotas futuras):
```python
@bp.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
```
Incluí também `Referrer-Policy: no-referrer` — não exigido pelo `selfcheck.py` nem pelas regras do `.zap/rules.tsv`, mas recomendado pela OWASP como defesa adicional para evitar que URLs internas (que podem conter identificadores de cliente) sejam vazadas via cabeçalho `Referer` para sites de terceiros.

Esta foi, deliberadamente, a **última** correção aplicada — conforme a ordem estratégica do guia, o ZAP só consegue avaliar os cabeçalhos HTTP depois que a aplicação consegue efetivamente inicializar no job dinâmico do pipeline, o que depende da imagem Docker já estar corrigida (F4).

**Validação local:** iniciei a aplicação localmente (Flask dev server) e confirmei via `curl -I`:
```
HTTP/1.1 200 OK
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: no-referrer
```
Todos os 4 cabeçalhos exigidos pelo `.zap/rules.tsv` (regras `10020`, `10021`, `10035`, `10038`) estão presentes.

---

## 3. Correções Após a 1ª Execução Real do Pipeline

As 7 correções acima foram validadas localmente com os binários reais das ferramentas, mas sem um daemon Docker disponível no ambiente de edição — ou seja, sem conseguir efetivamente *construir* a imagem e rodar o job `security-dynamic` completo. Após o `git push` e a primeira execução real do GitHub Actions, dois achados genuinamente novos apareceram — exatamente o tipo de feedback que só a pipeline real pode dar. Ambos foram corrigidos e commitados na sequência (e, como a seção 4 mostra, uma dessas duas correções precisou de uma segunda tentativa).

### Commit `2016b3e` — F4 (complemento): CVEs HIGH em `wheel` e `jaraco.context` na imagem construída

**O problema:** O Trivy Image scan real reportou:
```
Python (python-pkg)
Total: 2 (HIGH: 2, CRITICAL: 0)
jaraco.context  CVE-2026-23949  HIGH  5.3.0   → fixed 6.1.0
wheel           CVE-2026-24049  HIGH  0.45.1  → fixed 0.46.2
```
Essas duas bibliotecas **não aparecem em `requirements.txt`** — não são dependências da aplicação. `wheel` é uma ferramenta de empacotamento usada apenas durante a instalação de pacotes Python; `jaraco.context` é uma dependência transitiva do ecossistema `setuptools`. Ambas vêm do processo de *bootstrap* do `pip`/`setuptools`/`wheel` que a própria imagem oficial `python:3.11-slim` já traz pré-instalado (via `ensurepip`), nas versões que estavam vigentes quando essa imagem foi publicada pelo mantenedor oficial.

**Por que importa:** Isso ilustra um ponto importante de SCA (*Software Composition Analysis*) que vai além do `requirements.txt` do projeto: a superfície de vulnerabilidades de uma imagem Docker inclui **tudo** que está instalado nela, inclusive ferramentas de build que vieram "de fábrica" na imagem base e que o time de desenvolvimento nunca declarou explicitamente. Ignorar esse tipo de achado por "não ser código nosso" seria um erro de postura de segurança.

**Decisão técnica:** Como `wheel` e `jaraco.context` são usados exclusivamente em tempo de instalação/build (nunca importados pelo Flask, Werkzeug, Gunicorn ou pelo código da aplicação em tempo de execução), havia duas estratégias válidas: (a) remover completamente `pip`/`setuptools`/`wheel` da imagem final, já que nada em runtime depende deles; ou (b) atualizá-los para as versões corrigidas. Optei pela **opção (b)**, mais conservadora: sem conseguir construir e testar a imagem localmente (ambiente sem Docker), remover pacotes do núcleo do Python de forma especulativa poderia quebrar algum import indireto de `pkg_resources` em alguma dependência (padrão legado ainda comum em bibliotecas mais antigas) sem que eu tivesse como validar antes de pedir para a pipeline rodar de novo. A atualização cirúrgica resolve exatamente as duas CVEs reportadas com risco mínimo:
```dockerfile
&& python -m pip install --no-cache-dir --upgrade "wheel>=0.46.2" "jaraco.context>=6.1.0"
```
Registrei como item de acompanhamento a possibilidade de, numa segunda iteração já validada por um build real, remover essas ferramentas de build do runtime por completo — alinhado ao espírito original do "mandamento" que a própria Dockerfile vulnerável já citava ("pacotes de build desnecessários em produção").

**Validação local:** reexecutei o Hadolint (`exit code 0`) e toda a suíte `pytest`/`selfcheck` para garantir que a alteração não afetou nada além da camada de build da imagem.

> **Atualização (ver seção 4): esta correção não funcionou.** A 2ª execução real do pipeline reportou exatamente as mesmas versões não corrigidas (`wheel` 0.45.1, `jaraco.context` 5.3.0), provando que o `pip install --upgrade` não alcançou o diretório real onde essas duas bibliotecas estavam instaladas na imagem — algo que só a execução real do Trivy Image, contra a imagem de fato construída, poderia revelar, já que o ambiente de edição não tinha Docker para eu confirmar isso antes de pedir o próximo push.

### Commit `fe1ca32` — F5 (correção de causa raiz): CSP ausente especificamente em `/admin` (404)

**O problema:** O OWASP ZAP real reportou:
```
FAIL-NEW: Content Security Policy (CSP) Header Not Set [10038] x 1
    http://localhost:8080/admin (404 Not Found)
```
O interessante — e a razão de eu ter investigado a causa raiz em vez de apenas "adicionar o cabeçalho de novo" — é que o CSP **já estava implementado** desde o commit `d46848a` e funcionava corretamente em todas as rotas reais (`/`, `/health`, `/clients`, etc.). A falha aparecia **apenas** em `/admin`, uma URL que não corresponde a nenhuma rota registrada (as rotas reais são `/admin/users` e `/admin/users/<id>/role`).

**Causa raiz:** o hook estava registrado como `@bp.after_request`, ou seja, no nível do **blueprint** `main`, não da aplicação Flask como um todo. No Flask, um hook `after_request` de blueprint só é executado quando a requisição foi efetivamente roteada e processada *dentro daquele blueprint*. Quando a URL não casa com nenhuma rota registrada, o Flask devolve um 404 **antes** de o roteamento alcançar qualquer blueprint — portanto o hook nunca era chamado, e a resposta de erro saía sem nenhum cabeçalho de segurança. Esse é um erro sutil e comum: testar manualmente só as rotas "felizes" (que existem) esconde esse tipo de lacuna, que só um scanner DAST como o ZAP, testando também caminhos inexistentes, consegue revelar.

**Decisão técnica:** Movi o hook de `app/main.py` (blueprint) para dentro de `create_app()` em `app/__init__.py`, registrando-o como `@app.after_request` — isso garante que ele seja executado para **toda** resposta da aplicação, incluindo 404s, 500s e qualquer erro levantado antes do roteamento chegar a um blueprint. Aproveitei a mudança para adicionar também `Permissions-Policy` e `Cross-Origin-Embedder-Policy`, dois cabeçalhos que apareciam como `WARN-NEW` (não bloqueante) no mesmo relatório do ZAP — uma melhoria de baixo risco e custo zero, já que o hook estava sendo editado de qualquer forma.

**Validação local:** iniciei o servidor Flask e testei explicitamente **as duas situações** — uma rota real e uma inexistente — confirmando que ambas agora carregam o conjunto completo de cabeçalhos:
```
curl -I http://localhost:8092/admin   → HTTP/1.1 404 NOT FOUND  (7 cabeçalhos presentes)
curl -I http://localhost:8092/        → HTTP/1.1 200 OK         (7 cabeçalhos presentes)
```

---

## 4. Correções Após a 2ª Execução Real do Pipeline

### Commit `d2d2d1c` — F4 (correção definitiva): remoção completa de `pip`/`setuptools`/`wheel`/`jaraco.context`

**O problema:** a 2ª execução real do Trivy Image reportou **as mesmas 2 CVEs HIGH, nas mesmas versões exatas** (`wheel` 0.45.1, `jaraco.context` 5.3.0) do commit `2016b3e` — prova definitiva de que o upgrade cirúrgico não teve efeito algum na imagem real.

**Por que o upgrade falhou (análise, não apenas "tentei de novo"):** antes de simplesmente tentar outra variação do mesmo comando, investiguei a causa mais provável. A imagem oficial `python:3.11-slim` instala `pip`+`setuptools`+`wheel` via bootstrap `ensurepip`/`get-pip.py` durante a construção da própria imagem pelo mantenedor, com versões fixas e congeladas naquele momento — `jaraco.context` entra como dependência transitiva de `setuptools`. O ponto crítico: sem um daemon Docker disponível no ambiente onde fiz a correção, eu não conseguia inspecionar diretamente qual caminho exato do sistema de arquivos da imagem continha essas distribuições (`/usr/local/lib/python3.11/site-packages`? um local gerenciado separadamente por `apt`? algum efeito colateral do multi-stage?). O comando `pip install --upgrade` só tem efeito se apontar exatamente para onde o pacote já está instalado — e evidentemente não apontou.

**Decisão técnica — eliminar a ambiguidade em vez de adivinhar de novo:** ao invés de tentar uma terceira variação "mais específica" do comando de upgrade (continuando a apostar em acertar um caminho que eu não conseguia verificar), mudei de estratégia por completo: **remover inteiramente** `pip`, `setuptools`, `wheel` e `jaraco.context` do estágio final, em vez de atualizá-los. Essa abordagem tem uma propriedade importante que o upgrade não tinha: ela resolve o problema **independentemente de onde exatamente os pacotes estejam** — usei tanto `pip uninstall` (que resolve a localização pelo próprio mecanismo de bookkeeping do pip) quanto uma varredura direta do sistema de arquivos (`find` nos diretórios `site-packages`/`dist-packages` prováveis, removendo qualquer `wheel*`, `jaraco*`, `setuptools*` ou `pip*` encontrado), como camada de defesa redundante.

Antes de aplicar essa remoção, validei que ela era segura — o risco real de remover pacotes do núcleo do Python é quebrar alguma biblioteca que ainda dependa do padrão legado `pkg_resources` (de `setuptools`) para resolver sua própria versão em tempo de import. Testei isso diretamente, fora do Docker, no meu ambiente de validação:
```python
pip uninstall -y pip setuptools  # (wheel já não estava presente nesse venv de teste)
python -c "import flask, werkzeug, gunicorn, itsdangerous; print('imports OK')"
# imports OK
```
E, mais rigorosamente, subi um servidor Gunicorn real (o mesmo processo usado em produção pelo `ENTRYPOINT` do Dockerfile) sem `pip`/`setuptools` instalados e confirmei uma resposta HTTP 200 completa, com todos os cabeçalhos de segurança, no endpoint `/health`. Isso comprova, com evidência empírica e não apenas suposição, que esse conjunto específico de bibliotecas (Flask 3.1.2, Werkzeug 3.1.3, Gunicorn 23.0.0, itsdangerous 2.2.0) não tem nenhuma dependência oculta de `pkg_resources` em tempo de execução.

**Detalhe de qualidade do script:** a primeira versão do comando de remoção usava o padrão `COMANDO || true` dentro de uma cadeia `&&`, o que o Hadolint sinalizou (`SC2015`, nível informativo: "A && B || C não é um if-then-else"). Reescrevi a sequência usando `;` para separar os comandos (sem depender do código de saída do anterior) e um `true` final — eliminando o aviso por completo, sem depender de um threshold de severidade para "esconder" o problema.

**Validação local:** Hadolint voltou a `exit code 0` sem nenhum achado (nem mesmo o informativo anterior); `pytest -v` e `selfcheck --nivel 3` permaneceram verdes.

### Commit `83d7617` — F5 (complemento): 4 `WARN-NEW` do ZAP que também bloqueavam a Action

**O problema:** mesmo com o `FAIL-NEW` de CSP resolvido (commit `fe1ca32`), a Action do ZAP continuou falhando — porque `fail_action: true`, no `zaproxy/action-baseline`, propaga **qualquer** código de saída não-zero do `zap-baseline.py`, e esse script retorna código `2` quando existem `WARN` mesmo sem nenhum `FAIL`. Ou seja: a configuração atual do pipeline exige **zero alertas no total**, não apenas zero `FAIL`. Os 4 `WARN-NEW` reportados:
```
WARN-NEW: Storable and Cacheable Content [10049] x 5
WARN-NEW: Permissions Policy Header Not Set [10063] x 1
WARN-NEW: Cross-Origin-Embedder-Policy Header Missing or Invalid [90004] x 6
WARN-NEW: Sec-Fetch-Dest Header is Missing [90005] x 12
```

**Decisão técnica, achado a achado:**
- **[10049] Storable and Cacheable Content:** a API retorna dados de clientes "black tier" (nomes, telefones, endereços) sem nenhuma diretiva de cache — qualquer proxy ou navegador intermediário poderia armazenar essas respostas. Adicionei `Cache-Control: no-store, max-age=0` e `Pragma: no-cache` em toda resposta.
- **[10063] Permissions Policy Header Not Set:** adicionei `Permissions-Policy: geolocation=(), camera=(), microphone=()` — a API não usa nenhuma dessas capacidades do navegador, então o princípio de menor privilégio recomenda bloqueá-las explicitamente.
- **[90004] Cross-Origin-Embedder-Policy Header Missing:** adicionei `Cross-Origin-Embedder-Policy: require-corp` (viria a precisar de mais um complemento na rodada seguinte — ver seção 5).
- **[90005] Sec-Fetch-Dest Header is Missing:** antes de simplesmente adicionar "mais um cabeçalho", investiguei o que essa regra realmente verifica — consultei a documentação oficial do ZAP (`zaproxy.org/docs/alerts/90005-3`) e a implementação de referência (`FetchMetadataRequestHeadersScanRule`). Confirmei que `Sec-Fetch-Dest` é um cabeçalho que o **navegador** envia na requisição (não algo que o servidor devolve na resposta), e que o próprio scanner automatizado do ZAP Baseline não replica esse comportamento de navegador real ao rastrear a aplicação. Não existe nenhuma resposta HTTP do servidor que resolva esse achado — é uma limitação conhecida e documentada da ferramenta de scanning, não uma falha da aplicação. Documentei isso como exceção formal em `.zap/rules.tsv` (`90005 IGNORE`), seguindo exatamente o mesmo padrão de governança de risco que o guia da disciplina ensina para o `.trivyignore` (seção 4.3 do `docs/GUIA_TRILHA_3_TECNICA.md`): motivo técnico, responsável e data de revisão documentados no próprio arquivo.

Também adicionei as diretivas de CSP que não herdam de `default-src` (`object-src 'none'`, `base-uri 'self'`, `form-action 'self'`, `frame-ancestors 'none'`), antecipando a regra `10055` do ZAP (que veio a aparecer de fato na rodada seguinte, sem nunca ter sido vista nos meus testes locais).

**Validação local:** reiniciei o servidor e testei `curl -I` em uma rota real (`/`) e numa inexistente (`/admin`, 404), confirmando que todos os cabeçalhos aparecem em ambas as respostas — o que garante que o problema de causa raiz da seção 3 (hook de blueprint não cobrindo 404s) continua corrigido.

---

## 5. Correções Após a 3ª Execução Real do Pipeline

A 3ª execução revelou que as correções da seção 4 foram **parciais** em 2 pontos — um padrão interessante de se documentar, porque mostra os limites de validar headers de segurança sem o scanner real:

```
WARN-NEW: Non-Storable Content [10049] x 5
WARN-NEW: Cross-Origin-Resource-Policy Header Missing or Invalid [90004] x 4
FAIL-NEW: 0   WARN-NEW: 2   IGNORE: 1   PASS: 68
```

O `IGNORE: 1` confirma que a exceção de `90005` registrada na rodada anterior está sendo corretamente aplicada pelo ZAP.

### Commit `7c5e6bd` — F5 (complemento final)

**[90004] agora aponta para `Cross-Origin-Resource-Policy`, não mais para `Cross-Origin-Embedder-Policy`:** investigando por que a mesma regra `90004` continuava disparando depois de eu já ter adicionado COEP, descobri (documentação oficial do ZAP, `zaproxy.org/docs/alerts/90004`) que essa regra na verdade agrupa **3 sub-alertas distintos** sob o mesmo ID — `Cross-Origin-Resource-Policy`, `Cross-Origin-Embedder-Policy` e `Cross-Origin-Opener-Policy` — e reporta qualquer um dos três que estiver faltando. Eu já tinha adicionado COEP (rodada 2) e COOP (seção 3, junto com a correção do CSP), mas nunca CORP. Adicionei `Cross-Origin-Resource-Policy: same-origin`, completando o trio.

**[10049] mudou de "Storable and Cacheable Content" para "Non-Storable Content":** isso prova que o `Cache-Control: no-store` da rodada anterior **funcionou exatamente como pretendido** — a classificação mudou da pior categoria possível para a melhor. O que eu não sabia até pesquisar a fundo: a regra `10049` do ZAP sempre classifica qualquer resposta em uma de **3 categorias mutuamente exclusivas** (`10049-1` Non-Storable, `10049-2` Storable mas não cacheável, `10049-3` Storable e cacheável), e isso é documentado oficialmente (`zaproxy.org/docs/alerts/10049`) como 3 variantes informativas do mesmo relatório de cacheabilidade — ou seja, **qualquer resposta HTTP, com qualquer cabeçalho de cache, sempre vai cair em uma dessas 3 e gerar exatamente um alerta.** Não existe uma 4ª configuração de cabeçalho que resulte em "zero alertas" para essa regra. Como `Non-Storable` já é, por definição, a opção mais segura das três, documentei isso como exceção formal em `.zap/rules.tsv` (`10049 IGNORE`), com a mesma justificativa técnica detalhada de `90005`.

**Por que pesquisar antes de reagir importa aqui:** em ambas as correções desta seção, a tentação inicial seria "adicionar mais um cabeçalho e tentar de novo" sem entender o mecanismo da regra. Investigar a documentação oficial de cada regra do ZAP antes de decidir entre "corrigir" e "aceitar como exceção formal" é o que diferencia uma correção de causa raiz de um ciclo indefinido de tentativa-e-erro contra o scanner.

**Validação local:** `pytest -v` (7 passed) e `selfcheck --nivel 3` (SUCESSO) permanecem verdes; reconfirmado via `curl -I` que as 11 diretivas de cabeçalho agora presentes aparecem tanto em `/` (200) quanto em `/admin` (404).

---

## 6. Ajuste Adicional (não é uma das 7 falhas, mas decorre diretamente delas)

**Arquivo:** `tests/test_selfcheck.py`

Este teste, no estado original do repositório, afirmava explicitamente que `python scripts/selfcheck.py --nivel 3` deveria **falhar** (`returncode == 1`), pois seu propósito era validar que o script de autoavaliação detectava corretamente o baseline vulnerável. Esse teste é, por definição, incompatível com um repositório corrigido — depois de resolver F1 a F7, o selfcheck passa a retornar sucesso (`exit code 0`), o que é o comportamento desejado. Atualizei a asserção para refletir o estado remediado (`returncode == 0`, presença da string `"SUCESSO"`), documentando no próprio commit o motivo da mudança. Sem esse ajuste, `pytest -v` reportaria uma falha que não reflete nenhum problema real no código — apenas o fato de que o teste descrevia o estado "antes", não o estado "depois".

---

## 7. Resumo das Validações Executadas

Todas as correções foram validadas com as ferramentas reais do pipeline (não apenas inferidas), baixando os binários oficiais localmente e, para os achados das seções 3 a 5, confirmadas também por 3 execuções reais do GitHub Actions:

| Falha | Ferramenta | Resultado |
|---|---|---|
| F1 | Gitleaks v8.30.1 (`gitleaks dir`) | Sem segredos no conteúdo versionado |
| F2 | Trivy v0.76.1 (`trivy fs`) | `Total: 0 (HIGH: 0, CRITICAL: 0)` |
| F3 | Semgrep v1.182.1 (`--config auto`) | `0 findings` em `app/` |
| F4 | Hadolint v2.12.0 + **Trivy Image real (GitHub Actions, 2 rodadas)** | Exit code `0`; 2 CVEs HIGH em `wheel`/`jaraco.context` — upgrade cirúrgico falhou na 1ª tentativa, resolvidas com remoção completa das ferramentas de build na 2ª |
| F5 | `curl -I` (rota real e 404) + **ZAP Baseline real (GitHub Actions, 3 rodadas)** | 11/11 cabeçalhos presentes em ambos os casos; `FAIL-NEW` de CSP em `/admin` corrigido na raiz (hook movido para `@app.after_request`); 6 `WARN-NEW` adicionais resolvidos (Cache-Control, Permissions-Policy, CSP sem fallback, trio COEP/COOP/CORP); `Sec-Fetch-Dest` e cacheabilidade (`10049`) documentados como exceção formal (não corrigíveis via resposta do servidor) |
| F6 | `pytest` (`test_admin_routes`) | Verde — RBAC aplicado sem regressão |
| F7 | Semgrep v1.182.1 (`--config p/docker-compose`) | `0 findings` |
| Regressão geral | `pytest -v` (suíte completa) | `7 passed` |
| Gabarito do curso | `python scripts/selfcheck.py --nivel 3` | `SUCESSO: Todas as checagens da Trilha 3 passaram localmente!` |

---

## 8. Risco Residual e Próximos Passos

1. **Histórico do Git:** o segredo original de `.env` permanece nos commits anteriores a esta branch. Recomenda-se, como ação de acompanhamento (fora deste PR, por ser uma operação destrutiva de histórico), reescrever o histórico com `git-filter-repo` e forçar um novo push, coordenado previamente com qualquer colaborador do repositório.
2. **Lição sobre validar sem o ambiente real:** as 3 rodadas de feedback real do pipeline (seções 3 a 5) mostram o limite prático de corrigir Dockerfile/DAST sem acesso a um daemon Docker local — cada rodada revelou algo que a validação local (hadolint, semgrep, pytest, selfcheck, curl contra um servidor Flask de desenvolvimento) não tinha como prever, por testar camadas diferentes (imagem construída de fato, scanner DAST real). Isso não é falha da validação local — é o motivo pelo qual a pipeline de CI/CD existe como *quality gate* final, e por que vale a pena iterar com base no feedback real em vez de assumir que a validação local é suficiente.

Dois itens que constavam aqui como pendentes foram resolvidos depois da redação inicial deste documento:
- **Branch Protection Rules:** configurado em Settings → Branches do fork — a `main` agora exige Pull Request e pelo menos 1 aprovador antes de merge.
- **Confirmação do Trivy Image:** a execução final do pipeline (run #8, 100% verde, ver `docs/TEMPLATE_EVIDENCIAS.md` seção 3) confirma que o job `security-dynamic` — que inclui o Trivy Image scan — passou, validando que a remoção de `pip`/`setuptools`/`wheel`/`jaraco.context` (commit `d2d2d1c`) realmente eliminou as 2 CVEs HIGH na imagem construída.

## 9. SBOM (Software Bill of Materials)

Como item bônus (seção 6.1 do `docs/GUIA_TRILHA_3_TECNICA.md`), gerei o inventário formal de componentes em [`docs/sbom.cyclonedx.json`](docs/sbom.cyclonedx.json), padrão CycloneDX 1.6.

**Como foi gerado:** sem Docker disponível para rodar `trivy image --format cyclonedx` contra a imagem construída (o que o workflow de CI faz no job `security-dynamic`), usei a ferramenta oficial do próprio projeto CycloneDX, `cyclonedx-py`, apontada para um ambiente virtual limpo com apenas o `requirements.txt` final instalado — isso resolve a árvore de dependências real (diretas + transitivas) exatamente como ela existe no ambiente de execução da aplicação, incluindo licença declarada de cada pacote. Tive o cuidado de instalar o `cyclonedx-py` num venv **separado** do venv sendo escaneado — na primeira tentativa, rodar a ferramenta no mesmo ambiente em que ela própria estava instalada poluiu o SBOM com as dependências do gerador (43 componentes, incluindo coisas como `lxml`, `jsonschema`, `arrow` que não têm nada a ver com o Clube Aurora); corrigido apontando para um segundo venv isolado, resultando nos 11 componentes reais (10 da aplicação + `pip`, presente em qualquer venv por padrão, mas ausente da imagem de runtime final).

Nenhum componente apresenta CVE HIGH/CRITICAL (já confirmado pelo Trivy FS na seção 7).

---

*Documento gerado como parte da entrega da Trilha 3 (Técnica) do Projeto Final DevSecOps — Turma 1746, repositório `Clube Aurora`.*
