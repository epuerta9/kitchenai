set dotenv-load := true

# List all available commands
_default:
    @just --list --unsorted

# ----------------------------------------------------------------------
# DEPENDENCIES
# ----------------------------------------------------------------------

# Bootstrap local development environment
@bootstrap:
    hatch env create
    hatch env create dev
    hatch env create docs
    just install

# Setup local environnment (maybe install hatch and setup postgres (create database, etc..))
setup:
    #!/usr/bin/env bash
    just bootstrap
    # just run pre-commit install --install-hooks
    just migrate
    just createsuperuser
    just lint > /dev/null 2>&1 || true

# Install dependencies
@install:
    just run python --version

# Generate and upgrade dependencies
@upgrade:
    just run hatch-pip-compile --upgrade
    just run hatch-pip-compile dev --upgrade

# Clean up local development environment
@clean:
    hatch env prune
    rm -f .coverage.*

# ----------------------------------------------------------------------
# UTILITIES
# ----------------------------------------------------------------------

# Run a command within the dev environnment
@run *ARGS:
    hatch --env dev run {{ ARGS }}

# Get the full path of a hatch environment
@env-path ENV="dev":
    hatch env find {{ ENV }}

# ----------------------------------------------------------------------
# TESTING/TYPES
# ----------------------------------------------------------------------

# Run the test suite, generate code coverage, and export html report
@coverage-html: test
    rm -rf htmlcov
    @just run python -m coverage html --skip-covered --skip-empty

# Run the test suite, generate code coverage, and print report to stdout
coverage-report: test
    @just run python -m coverage report

# Run tests using pytest
@test *ARGS:
    just run coverage run -m pytest {{ ARGS }}

# Run mypy on project
@types:
    just run python -m mypy .

# Run the django deployment checks
@deploy-checks:
    just dj check --deploy

# ----------------------------------------------------------------------
# DJANGO
# ----------------------------------------------------------------------

# Run a falco command
@falco *COMMAND:
    just run falco {{ COMMAND }}

# Run a django management command
@dj *COMMAND:
    just run python -m manage {{ COMMAND }}

# Run the django development server
@server ADDRESS="":
    just falco work {{ ADDRESS }}

# Kill the django development server in case the process is running in the background
@kill-server PORT="8000":
    lsof -i :{{ PORT }} -sTCP:LISTEN -t | xargs -t kill

# Open a Django shell using django-extensions shell_plus command
@shell:
    just dj shell_plus

alias mm := makemigrations

# Generate Django migrations
@makemigrations *APPS:
    just dj makemigrations {{ APPS }}

# Run Django migrations
@migrate *ARGS:
    just dj migrate {{ ARGS }}

# Reset the database
@reset-db:
    just dj reset_db --noinput

alias su := createsuperuser

# Quickly create a superuser with the provided credentials
createsuperuser EMAIL="admin@localhost" PASSWORD="admin":
    #!/usr/bin/env bash
    set -euo pipefail
    email="{{ EMAIL }}"
    export DJANGO_SUPERUSER_PASSWORD='{{ PASSWORD }}'
    export DJANGO_SUPERUSER_USERNAME="${email%%@*}"
    just dj createsuperuser --noinput --email "{{ EMAIL }}"

# Generate admin code for a django app
@admin APP:
    just dj admin_generator {{ APP }} | tail -n +2 > kitchenai/{{ APP }}/admin.py

# Collect static files
@collectstatic:
    just dj collectstatic --no-input --skip-checks
    just dj compress

# ----------------------------------------------------------------------
# DOCS
# ----------------------------------------------------------------------

# Build documentation using Sphinx
@docs-build LOCATION="docs/_build/html":
    hatch run docs:sphinx-build docs {{ LOCATION }}

# Install documentation dependencies
@docs-install:
    hatch run docs:python --version

# Serve documentation locally
@docs-serve:
    hatch run docs:sphinx-autobuild docs docs/_build/html --port 8001

# Generate and upgrade documentation dependencies
docs-upgrade:
    just run hatch-pip-compile dev --upgrade


# ----------------------------------------------------------------------
# LINTING / FORMATTING
# ----------------------------------------------------------------------

# Run all formatters
@fmt:
    just --fmt --unstable
    hatch fmt --formatter
    just run pre-commit run pyproject-fmt -a  > /dev/null 2>&1 || true
    just run pre-commit run reorder-python-imports -a  > /dev/null 2>&1 || true
    just run pre-commit run djade -a  > /dev/null 2>&1 || true

# Run pre-commit on all files
@lint:
    hatch --env dev run pre-commit run --all-files

# ----------------------------------------------------------------------
# BUILD UTILITIES
# ----------------------------------------------------------------------

# Bump project version and update changelog
#bumpver VERSION:
#deprecated: we manage the versions manually via __about__.py
#just run bump-my-version bump {{ VERSION }}
bumpver:
    #!/usr/bin/env bash
    set -euo pipefail
    just run git-cliff --output CHANGELOG.md

    if [ -z "$(git status --porcelain)" ]; then
        echo "No changes to commit."
        git push && git push --tags
        exit 0
    fi

    version="$(hatch version)"
    git add CHANGELOG.md
    git commit -m "Generate changelog for version ${version}"
    git tag -f "v${version}"
    git push && git push --tags

# Build a wheel distribution of the project using hatch
build-wheel:
    #!/usr/bin/env bash
    set -euo pipefail
    just dj tailwind --skip-checks build
    export DEBUG="False"
    just collectstatic
    hatch build

# Build a binary distribution of the project using hatch / pyapp
build-bin:
    #!/usr/bin/env bash
    current_version=$(hatch version)
    wheel_path="${PWD}/dist/kitchenai-${current_version}-py3-none-any.whl"
    [ -f "$wheel_path" ] || { echo "Wheel file does not exist. Please build the wheel first using the 'buildwheel' recipe."; exit 1; }
    export PYAPP_UV_ENABLED="1"
    export PYAPP_PYTHON_VERSION="3.12"
    export PYAPP_FULL_ISOLATION="1"
    export PYAPP_EXPOSE_METADATA="1"
    export PYAPP_PROJECT_NAME="kitchenai"
    export PYAPP_PROJECT_VERSION="${current_version}"
    export PYAPP_PROJECT_PATH="${wheel_path}"
    export PYAPP_DISTRIBUTION_EMBED="1"
    # Add extra packages here, separated by spaces
    export PYAPP_EXTRA_PACKAGES="deepeval_plugin>=0.2.1"
    hatch build -t binary

# Build linux binary in docker
build-linux-bin:
    mkdir dist || true
    docker build -t build-bin-container . -f deploy/Dockerfile.binary
    docker run -it -v "${PWD}:/app" -w /app --name final-build build-bin-container just build-wheel && just build-bin
    docker cp final-build:/app/dist .
    docker rm -f final-build


# Build docker image
build-docker-image:
    #!/bin/bash
    current_version=$(hatch version) && \
    image_name="kitchenai-bundle" && \
    just install && \
    docker build -t "${image_name}:${current_version}" -f deploy/Dockerfile . && \
    docker tag "${image_name}:${current_version}" "${image_name}:latest" && \
    docker tag "${image_name}:${current_version}" "epuerta18/${image_name}:latest" && \
    docker tag "${image_name}:${current_version}" "epuerta18/${image_name}:${current_version}" && \
    echo "Built docker image ${image_name}:${current_version}"

# Build slim docker image
build-docker-image-slim:
    #!/bin/bash
    current_version=$(hatch version) && \
    image_name="kitchenai-slim" && \
    just install && \
    docker build -t "${image_name}:${current_version}" -f deploy/Dockerfile.slim . && \
    docker tag "${image_name}:${current_version}" "${image_name}:latest" && \
    docker tag "${image_name}:${current_version}" "epuerta18/${image_name}:latest" && \
    docker tag "${image_name}:${current_version}" "epuerta18/${image_name}:${current_version}" && \
    echo "Built slim docker image ${image_name}:${current_version}"


push-docker-image:
    #!/usr/bin/env bash
    set -euo pipefail
    current_version=$(hatch version)
    image_name="kitchenai-bundle"
    docker tag "${image_name}:${current_version}" "${image_name}:latest"
    docker push "epuerta18/${image_name}:latest"
    docker push "epuerta18/${image_name}:${current_version}"
    echo "Pushed docker image epuerta18/${image_name}:${current_version}"

push-docker-image-slim:
    #!/usr/bin/env bash
    set -euo pipefail
    current_version=$(hatch version)
    image_name="kitchenai-slim"
    docker tag "${image_name}:${current_version}" "${image_name}:latest"
    docker push "epuerta18/${image_name}:latest"
    docker push "epuerta18/${image_name}:${current_version}"
    echo "Pushed docker image epuerta18/${image_name}:${current_version}"


prune-docker:
    # Stop and remove containers, networks, volumes, and images
    docker compose down --volumes --rmi all --remove-orphans

    # To be extra thorough, you can also:
    # Remove all unused volumes
    docker volume prune -f

    # Remove all unused containers
    docker container prune -f

    # Remove all unused images
    docker image prune -a -f