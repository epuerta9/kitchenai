# Stage 1: Use the kitchenai base image
FROM kitchenai:latest

# Set up environment variables
ENV PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    PYTHONPATH="/app" \
    PATH="$VENV_PATH/bin:$PATH"

# Copy additional dependencies (e.g., wheel files) into the container
COPY dist/ /tmp

# Install additional dependencies into the existing virtual environment
WORKDIR /tmp
RUN python -m ensurepip && \
    python -m pip install /tmp/*.whl

# Copy the kitchenai configuration file
COPY kitchenai.yml /app/kitchenai.yml
 
# Set the working directory
WORKDIR /app

# Run migrations and setup tasks using the existing manage.py script
RUN . $VENV_PATH/bin/activate && \
    python manage.py migrate && \
    python manage.py setup_periodic_tasks

# Initialize the application
RUN . $VENV_PATH/bin/activate && python manage.py init

# Expose the application port
EXPOSE 8000

# Use the init system defined in the base image
ENTRYPOINT ["/init"]
