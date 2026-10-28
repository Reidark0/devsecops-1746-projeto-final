"""Fábrica da aplicação Clube Aurora."""

import os
from pathlib import Path

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("DATABASE", str(Path(app.instance_path) / "aurora.db")),
        SEED_PASSWORD=os.environ.get("SEED_PASSWORD", "dev-only-change-me"),
    )
    if test_config:
        app.config.update(test_config)

    db_path = Path(app.config["DATABASE"])
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        app.config["DATABASE"] = str(Path("/tmp") / "aurora.db")

    app.teardown_appcontext(db.close_db)

    @app.after_request
    def set_security_headers(response):
        # Registrado no nível da aplicação (não do blueprint) para cobrir
        # também respostas de erro (404/500) que nunca chegam a ser roteadas
        # para dentro do blueprint "main" — ex.: GET /admin sem rota definida.
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # object-src/base-uri/form-action/frame-ancestors declarados explicitamente
        # (regra ZAP 10055: diretivas sem fallback para default-src).
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        # API retorna dados de clientes VIP: nunca deve ficar em cache de
        # proxies/navegador (regra ZAP 10049: Storable and Cacheable Content).
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
        return response

    from .main import bp

    app.register_blueprint(bp)

    @app.cli.command("init-db")
    def init_db_command():
        """Recria o banco com dados de exemplo."""
        db.init_db()
        print("Banco inicializado.")

    with app.app_context():
        if not Path(app.config["DATABASE"]).exists() or os.path.getsize(app.config["DATABASE"]) == 0:
            db.init_db()

    return app
