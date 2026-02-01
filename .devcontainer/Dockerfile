# This image has selenium and chrome driver already installed
FROM quay.io/rofrano/pipeline-selenium:sp26

# Become a regular user for development
ARG USERNAME=vscode
USER $USERNAME

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp; bash ./install-tools.sh

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --dev
