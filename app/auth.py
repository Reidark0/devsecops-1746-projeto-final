"""Autenticação por token assinado e controle de acesso por papel."""

from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from . import db

TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60  # um turno de trabalho


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="aurora-auth")


def issue_token(user_id):
    return _serializer().dumps({"uid": user_id})


def authenticate(email, password):
    """Retorna o usuário se as credenciais forem válidas; caso contrário, None."""
    user = db.get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        db.log_action(user["id"] if user else None, f"login_failed:{email}")
        return None
    db.log_action(user["id"], "login_ok")
    return user


def _load_user_from_request():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        data = _serializer().loads(header[7:], max_age=TOKEN_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    return db.get_user_by_id(data.get("uid"))


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = _load_user_from_request()
        if user is None:
            return jsonify(error="autenticação necessária"), 401
        g.user = user
        return view(*args, **kwargs)

    return wrapper


def require_role(role):
    """Exige autenticação e o papel informado."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if g.user["role"] != role:
                return jsonify(error="acesso negado"), 403
            return view(*args, **kwargs)

        return wrapper

    return decorator
