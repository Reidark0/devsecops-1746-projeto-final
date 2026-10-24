#!/usr/bin/env python3
"""
selfcheck.py — Validador Local de Autoavaliação do Aluno (Clube Aurora)
Permite ao aluno validar localmente o progresso das correções antes de abrir Pull Request.

Uso:
    python scripts/selfcheck.py --nivel 2
    python scripts/selfcheck.py --nivel 3
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Configurar stdout para UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Cores ANSI para saída no terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def check_f1(root_dir: Path) -> tuple[bool, str]:
    """F1: Segredos e credenciais expostos no .env."""
    env_file = root_dir / ".env"
    gitignore_file = root_dir / ".gitignore"

    if env_file.exists():
        content = env_file.read_text(encoding="utf-8", errors="ignore")
        if "aurora-super-secret-key-production-hardcoded-2026" in content or "AuroraAdminMaster#2026!" in content:
            return False, "F1 Segredos em .env — Dica: Remova as credenciais hardcoded do arquivo .env ou exclua-o do versionamento e garanta que '.env' esteja no .gitignore."

    if gitignore_file.exists():
        gitignore_content = gitignore_file.read_text(encoding="utf-8", errors="ignore")
        if ".env" not in gitignore_content:
            return False, "F1 Segredos em .env — Dica: Adicione o padrão '.env' ao arquivo .gitignore para evitar vazamento acidental de chaves locais."
    else:
        return False, "F1 Segredos em .env — Dica: Crie o arquivo .gitignore incluindo '.env'."

    return True, "F1 Segredos em .env: Credenciais protegidas e .env ignorado pelo git."


def check_f2(root_dir: Path) -> tuple[bool, str]:
    """F2: Dependências vulneráveis em requirements.txt."""
    req_file = root_dir / "requirements.txt"
    if not req_file.exists():
        return False, "F2 Dependências — Dica: requirements.txt não encontrado na raiz do projeto."

    content = req_file.read_text(encoding="utf-8", errors="ignore")
    vulnerable_patterns = [
        r"flask\s*==\s*2\.",
        r"werkzeug\s*==\s*2\.",
        r"gunicorn\s*==\s*20\.",
        r"urllib3\s*==\s*1\.26\.",
    ]
    for pattern in vulnerable_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, "F2 Dependências vulneráveis — Dica: Atualize as versões das bibliotecas em requirements.txt para mitigar CVEs conhecidas (consulte o Guia da Trilha)."

    return True, "F2 Dependências: Bibliotecas atualizadas para versões sem vulnerabilidades críticas conhecidas."


def check_f3(root_dir: Path) -> tuple[bool, str]:
    """F3: SQL Injection por concatenação de strings em app/db.py."""
    db_file = root_dir / "app" / "db.py"
    if not db_file.exists():
        return False, "F3 SQL Injection — Dica: Arquivo app/db.py não encontrado."

    content = db_file.read_text(encoding="utf-8", errors="ignore")
    if re.search(r'f["\'].*SELECT.*LIKE\s+.*\{name\}', content, re.IGNORECASE):
        return False, "F3 SQL Injection — Dica: Em app/db.py, substitua a interpolação direta de f-string por consulta parametrizada usando placeholders '?' do SQLite."

    if "?" not in content:
        return False, "F3 SQL Injection — Dica: Utilize placeholders '?' na consulta SQL de busca para garantir a parametrização segura."

    return True, "F3 SQL Injection: Consulta parametrizada com sucesso em app/db.py."


def check_f4(root_dir: Path) -> tuple[bool, str]:
    """F4: Hardening de Dockerfile (4 mandamentos)."""
    dockerfile = root_dir / "Dockerfile"
    if not dockerfile.exists():
        return False, "F4 Hardening Dockerfile — Dica: Dockerfile não encontrado na raiz."

    content = dockerfile.read_text(encoding="utf-8", errors="ignore")
    if "python:latest" in content:
        return False, "F4 Hardening Dockerfile — Dica: Evite a tag mutável :latest na instrução FROM. Utilize uma imagem base estável (ex: python:3.11-slim)."

    if "USER" not in content or "USER root" in content:
        return False, "F4 Hardening Dockerfile — Dica: Configure a execução do contêiner sob um usuário sem privilégios (ex: USER nonroot)."

    if "AS builder" not in content and "as builder" not in content:
        return False, "F4 Hardening Dockerfile — Dica: Implemente Multi-stage build para separar o ambiente de compilação do runtime de produção."

    return True, "F4 Hardening Dockerfile: Boas práticas e mandamentos de container seguro aplicados."


def check_f5(root_dir: Path) -> tuple[bool, str]:
    """F5: Cabeçalhos HTTP de segurança defensivos."""
    main_file = root_dir / "app" / "main.py"
    init_file = root_dir / "app" / "__init__.py"

    content = ""
    if main_file.exists():
        content += main_file.read_text(encoding="utf-8", errors="ignore") + "\n"
    if init_file.exists():
        content += init_file.read_text(encoding="utf-8", errors="ignore") + "\n"

    if not content:
        return False, "F5 Cabeçalhos HTTP — Dica: Arquivos app/main.py e app/__init__.py não encontrados."

    required_headers = ["X-Content-Type-Options", "X-Frame-Options"]
    for h in required_headers:
        if h not in content:
            return False, f"F5 Cabeçalhos HTTP — Dica: Registre o cabeçalho defensivo '{h}' nas respostas da aplicação (ex: via @app.after_request)."

    return True, "F5 Cabeçalhos HTTP: Cabeçalhos defensivos (X-Content-Type-Options, X-Frame-Options) registrados."


def check_f6(root_dir: Path) -> tuple[bool, str]:
    """F6: Princípio do menor privilégio em db.py e main.py."""
    db_file = root_dir / "app" / "db.py"
    main_file = root_dir / "app" / "main.py"

    if not db_file.exists():
        return False, "F6 Menor Privilégio — Dica: app/db.py não encontrado."
    if not main_file.exists():
        return False, "F6 Menor Privilégio — Dica: app/main.py não encontrado."

    content_db = db_file.read_text(encoding="utf-8", errors="ignore")
    if 'role="admin"' in content_db:
        return False, "F6 Menor Privilégio — Dica: Em app/db.py na função create_user, o papel padrão deve ser 'staff', nunca 'admin'."

    content_main = main_file.read_text(encoding="utf-8", errors="ignore")
    pattern = r'@bp\.post\(["\']/admin/users/<int:user_id>/role["\']\)\s*@auth\.require_role\(["\']admin["\']\)\s*def admin_set_role'
    if not re.search(pattern, content_main):
        return False, "F6 Menor Privilégio — Dica: Em app/main.py, proteja o endpoint admin_set_role garantindo que apenas administradores autenticados alterem papéis (@auth.require_role('admin') após @bp.post)."

    return True, "F6 Menor Privilégio: Papel padrão restrito e controle de autorização RBAC aplicado."


def check_f7(root_dir: Path) -> tuple[bool, str]:
    """F7: Segurança em Infraestrutura como Código (docker-compose.yml)."""
    compose_file = root_dir / "docker-compose.yml"
    if not compose_file.exists():
        return True, "F7 IaC Security: docker-compose.yml não presente."

    content = compose_file.read_text(encoding="utf-8", errors="ignore")
    if "privileged: true" in content or "privileged: yes" in content:
        return False, "F7 IaC Security — Dica: Remova a diretiva 'privileged: true' no serviço do docker-compose.yml."

    if "/var/run/docker.sock" in content:
        return False, "F7 IaC Security — Dica: Desmonte o socket do host Docker (/var/run/docker.sock) do contêiner da aplicação."

    return True, "F7 IaC Security: Configurações de container privilegiado e montagem de socket eliminadas."


def main():
    parser = argparse.ArgumentParser(
        description="Script de autoavaliação e verificação local para o Projeto Final (Clube Aurora)."
    )
    parser.add_argument(
        "--trilha",
        "--nivel",
        dest="trilha",
        choices=["2", "3"],
        default="3",
        help="Trilha escolhida: 2 (Mista: F1, F2, F4) ou 3 (Técnica: F1 a F7). Padrão: 3.",
    )
    parser.add_argument(
        "--dir",
        default=None,
        help="Diretório raiz da aplicação (padrão: raiz do repositório).",
    )
    args = parser.parse_args()

    if args.dir:
        repo_root = Path(args.dir).resolve()
    else:
        # A pasta scripts/ fica logo abaixo da raiz do fork
        repo_root = Path(__file__).resolve().parent.parent

    print(f"\n============================================================")
    print(f" CLUBE AURORA — AUTOAVALIAÇÃO LOCAL (TRILHA {args.trilha})")
    print(f" Diretório auditado: {repo_root}")
    print(f"============================================================\n")

    if args.trilha == "2":
        selected_checks = [
            ("F1", check_f1),
            ("F2", check_f2),
            ("F4", check_f4),
        ]
    else:
        selected_checks = [
            ("F1", check_f1),
            ("F2", check_f2),
            ("F3", check_f3),
            ("F4", check_f4),
            ("F5", check_f5),
            ("F6", check_f6),
            ("F7", check_f7),
        ]

    failures = 0
    for flaw_id, check_func in selected_checks:
        passed, msg = check_func(repo_root)
        if passed:
            print(f"{GREEN}[OK]{RESET} {msg}")
        else:
            print(f"{RED}[  ]{RESET} {msg}")
            failures += 1

    print(f"\n------------------------------------------------------------")
    if failures == 0:
        print(f"{GREEN}SUCESSO: Todas as checagens da Trilha {args.trilha} passaram localmente!{RESET}")
        print("Você está pronto para realizar commit, enviar branch e abrir o Pull Request.")
        print(f"------------------------------------------------------------\n")
        sys.exit(0)
    else:
        print(f"{YELLOW}ATENÇÃO: {failures} item(ns) pendente(s) de ajuste na Trilha {args.trilha}.{RESET}")
        print("Siga as dicas acima para ajustar o código antes de submeter.")
        print(f"------------------------------------------------------------\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
