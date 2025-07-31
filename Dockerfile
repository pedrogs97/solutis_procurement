FROM python:3.11-slim-bullseye

# Create application directory
RUN mkdir -p /app/src
RUN mkdir -p /storage

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app"

# Copy dependency files
COPY ./poetry.lock /app/
COPY ./pyproject.toml /app/
COPY ./manage.py /app/
COPY ./config /app/config
COPY ./src /app/src

WORKDIR /app

# Install system packages and configure locale
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    locales \
    pkg-config \
    python3-dev \
    && sed -i '/^# pt_BR.UTF-8 UTF-8/s/^# //' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=pt_BR.UTF-8 \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry self add poetry-plugin-export \
    && poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt \
    && pip install --no-cache-dir uvicorn[standard] \
    && pip uninstall poetry -y \
    && rm requirements.txt \
    && chmod -R 755 /var \
    && apt-get remove -y curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r django \
    && useradd --no-log-init -r -g django django \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app \
    && chown -R django:django /storage

# Set locale environment
ENV LANG=pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8
