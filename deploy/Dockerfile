# Stage 1: General enviroment
FROM python:3.12-slim-bookworm AS python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    TAILWIND_CLI_PATH="/opt/tailwind" \
    PYTHONPATH="/app"

ENV PATH="$VENV_PATH/bin:$PATH"

# Stage 2: Install dependencies & build static files
FROM python-base as builder-base

# Install dependencies
WORKDIR $PYSETUP_PATH
COPY ./requirements.txt ./
RUN pip install --upgrade pip uv \
 && python -m uv venv $VENV_PATH && uv pip install -r requirements.txt

# install plugins here
#i.e RUN uv pip install "deepeval_plugin>=0.2.1"

# Create base requirements file
RUN uv pip list > "$VENV_PATH/base-requirements.txt"

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential nodejs npm --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Build static files
COPY . /app
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/kitchenai/static /app/kitchenai/staticfiles

RUN npm install -D daisyui
RUN python manage.py tailwind build
RUN python manage.py collectstatic --no-input --skip-checks --clear
RUN python manage.py compress

# Stage 3: Run service
FROM python-base as production

# Install uv in the production stage
RUN pip install --upgrade pip uv

# Copy files from builder
COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY --from=builder-base /app/kitchenai/staticfiles /app/kitchenai/staticfiles
COPY --from=builder-base /app/kitchenai/static /app/kitchenai/static
COPY kitchenai /app/kitchenai
COPY manage.py /app/manage.py

WORKDIR /app

EXPOSE 8001

# Add entrypoint script
COPY deploy/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
