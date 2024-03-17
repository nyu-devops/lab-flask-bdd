##################################################
# Create production image
##################################################
FROM python:3.11-slim

# Establish a working folder
WORKDIR /app

# Establish dependencies
COPY pyproject.toml poetry.lock ./
RUN python -m pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

# Copy source files last because they change the most
COPY wsgi.py .
COPY service ./service

# Switch to a non-root user and set file ownership
RUN useradd --uid 1001 flask && \
    chown -R flask:flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP=wsgi:app
ENV PORT 8080
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]
