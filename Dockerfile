# Dockerfile for Pay Shield Analytics Streamlit app (src/form)
# ------------------------------------------------------------
# Base image – lightweight Python 3.11
FROM python:3.11-slim

# Metadata (optional but useful for registries)
LABEL maintainer="Italo <ifvnasc@gmail.com>"
LABEL org.opencontainers.image.title="pay_shield_form"
LABEL org.opencontainers.image.description="Streamlit app for Pay Shield Analytics"
LABEL org.opencontainers.image.source="https://github.com/your-repo/pay_shield_analytics"

# Environment variables – keep Python output unbuffered and avoid .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

# Install OS‑level packages needed for building Python deps (e.g., pandas, numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libssl-dev \
        libffi-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file from src/form (ensures it's present)
COPY src/form/requirements.txt /app/requirements.txt
# Install Python dependencies
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the application source code (entire src/ directory)
COPY src/ /app/src/

# Expose the default Streamlit port
EXPOSE 8501

# Entrypoint – run Streamlit in headless mode on the configured port
CMD ["streamlit", "run", "src/form/app.py", "--server.headless", "true", "--server.port", "8501"]
