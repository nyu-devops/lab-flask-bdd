##################################################
# Create a builder image to compile in
##################################################
FROM python:3.11-slim as builder

# Added libraries for PostgreSQL before pip install
RUN apt-get update && apt-get install -y gcc libpq-dev

# Create working folder and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN python -m venv venv && \
    . /app/venv/bin/activate && \
    pip install -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt

##################################################
# Create production image from builder image
##################################################
FROM python:3.11-slim

# Install Postgres libraries
RUN apt-get update && apt-get install -y postgresql-client
# libpq-dev

# Establish working folder and copy dependencies
WORKDIR /app
COPY --from=builder /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH

# Copy the application contents
COPY service/ ./service/

# Switch to a non-root user and set file ownership
RUN useradd --uid 1001 flask && \
    chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP=service:app
ENV PORT 8080
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "service:app"]
