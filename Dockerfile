# ============================================================
# HireSense – Dockerfile
# ============================================================
# Single image shared by all three portal services (admin / hr / candidate).
# The APP_ROLE environment variable selects which portal to run.
# ============================================================

FROM python:3.11-slim

# --- System dependencies ---------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory -------------------------------------------------------
WORKDIR /app

# --- Python dependencies (cached layer) -------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Application source ------------------------------------------------------
COPY . .

# --- Entrypoint --------------------------------------------------------------
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose all three portal ports (the compose file binds each service to one)
EXPOSE 5010 5011 5012

ENTRYPOINT ["/entrypoint.sh"]
