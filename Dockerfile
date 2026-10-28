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
    # wheel e jaraco.context vêm do bootstrap de pip/setuptools da imagem
    # base (ensurepip), não de requirements.txt — são ferramentas de build,
    # nunca importadas pela aplicação em runtime. Atualizadas aqui para as
    # versões corrigidas (CVE-2026-24049 / CVE-2026-23949) reportadas pelo
    # Trivy Image scan.
    && python -m pip install --no-cache-dir --upgrade "wheel>=0.46.2" "jaraco.context>=6.1.0"

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
