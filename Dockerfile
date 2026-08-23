FROM python:3.12-alpine

LABEL org.opencontainers.image.title="odoo-health-check" \
      org.opencontainers.image.description="Audite une instance Odoo publique : indexabilité, exposition, sécurité." \
      org.opencontainers.image.url="https://jaikin.eu" \
      org.opencontainers.image.source="https://github.com/Jaikin-SASU/odoo-health-check" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && adduser -D -u 10001 auditor
USER auditor

ENTRYPOINT ["odoo-health-check"]
CMD ["--help"]
