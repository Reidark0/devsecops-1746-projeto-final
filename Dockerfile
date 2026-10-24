# ❌ DOCKERFILE INSEGURO (VIOLAÇÃO DOS 4 MANDAMENTOS DO HARDENING)
# 1. Não usa multi-stage build (imagem pesada)
# 2. Usa tag :latest mutável
# 3. Executa como ROOT por padrão
# 4. Sem declaração de HEALTHCHECK
FROM python:latest

WORKDIR /app

# Copia tudo de uma vez
COPY . /app

# Instalação com pacotes de build desnecessários em produção
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
