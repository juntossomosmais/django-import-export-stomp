FROM python:3.10-slim

WORKDIR /app

# Creates an appuser and change the ownership of the application's folder
RUN useradd appuser \
    && chown appuser ./

# Installs poetry and pip
RUN pip install --upgrade pip && \
    pip install poetry

# Copy dependency definition to cache
COPY --chown=appuser poetry.lock pyproject.toml ./

# Installs projects dependencies as a separate layer
RUN poetry export -f requirements.txt -o requirements.txt && \
    pip uninstall --yes poetry && \
    pip install --require-hashes -r requirements.txt

COPY --chown=appuser . ./

EXPOSE 8080

# Switching to the non-root appuser for security
USER appuser
