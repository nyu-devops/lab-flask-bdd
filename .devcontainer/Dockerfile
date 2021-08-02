# Image for a Python 3 development environment
FROM python:3.8-slim

# Add any tools that are needed beyond Python 3.7
RUN apt-get update \
    && apt-get install -y sudo git tree curl wget jq python3-selenium \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Create a user for development
ARG USERNAME=devops
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && usermod -aG sudo $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up the development environment
WORKDIR /workspace

# Add the IBM Cloud CLI
RUN if [ $(uname -m) != aarch64 ]; then \
        wget -O bluemix-cli.tar.gz https://clis.cloud.ibm.com/download/bluemix-cli/1.4.0/linux64 && \
        tar xzf bluemix-cli.tar.gz && \
        cd Bluemix_CLI/ && \
        ./install && \
        cd .. && \
        rm -fr Bluemix_CLI/ bluemix-cli.tar.gz && \
        ibmcloud cf install; \
    else \
        echo "aarch64 not supported"; \
    fi;

# Establish Python dependencies
COPY requirements.txt .
RUN pip install -U pip && \
    pip --no-cache-dir install -r requirements.txt

EXPOSE 8080

# Become a regular user
USER $USERNAME
