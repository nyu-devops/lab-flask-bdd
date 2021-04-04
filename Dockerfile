# Start with a Linux micro-container to keep the image tiny
FROM alpine:3

# Document who is responsible for this image
LABEL MAINTAINER="John Rofrano <rofrano@us.ibm.com>"

# Install just the Python runtime (no dev)
RUN apk --no-cache add \
    python3 \
    py3-pip

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD . .

# Expose any ports the app is expecting in the environment
ENV PORT 8080
EXPOSE $PORT

# Run the service
ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--workers=1", "--log-level=info", "service:app"]
