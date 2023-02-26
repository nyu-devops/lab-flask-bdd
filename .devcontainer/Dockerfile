# This image has selenium and chrome driver already installed
FROM rofrano/pipeline-selenium:latest

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp; bash ./install-tools.sh
