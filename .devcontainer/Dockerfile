# This image has selenium and chrome driver already installed
FROM rofrano/pipeline-selenium:latest

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp; bash ./install-tools.sh

# Add Python package requiremnets to the dev environment
WORKDIR /app
COPY requirements.txt .
RUN sudo pip install -U pip wheel && \
    sudo pip install -r requirements.txt
