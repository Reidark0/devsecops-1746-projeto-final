# ✅ Dockerfile endurecido (multi-stage, imagem fixada, usuário não-root, healthcheck)

FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 10001 -m nonroot \
    # pip/setuptools/wheel (e a dependência transitiva jaraco.context) vêm
    # do bootstrap da imagem base (ensurepip) e nunca são importados pela
    # aplicação em runtime (confirmado: flask/werkzeug/gunicorn/itsdangerous
    # rodam normalmente sem eles). Em vez de só atualizar as duas libs
    # flagradas pelo Trivy Image (CVE-2026-24049 em wheel, CVE-2026-23949
    # em jaraco.context), removemos as ferramentas de build inteiras do
    # runtime — elimina a CVE independente de qual diretório elas ocupam.
    && python -m pip uninstall -y wheel jaraco.context setuptools pip ; \
    find /usr/local/lib/python3*/ /usr/lib/python3*/ -maxdepth 2 \
        \( -iname "wheel*" -o -iname "jaraco*" -o -iname "setuptools*" -o -iname "pip-*" -o -iname "pip" \) \
        -exec rm -rf {} + 2>/dev/null; \
    true

WORKDIR /app

COPY --from=builder /root/.local /home/nonroot/.local
COPY . /app

RUN mkdir -p /app/instance \
    && chown -R nonroot:nonroot /app

ENV PATH=/home/nonroot/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

USER nonroot

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
