#!/bin/bash
#
# Setup the lab environment after container is started using:
#   "postCreateCommand": "bash /app/.devcontainer/scripts/setup-lab.sh"
# 
echo "**********************************************************************"
echo "Setting up Flask BDD lab environment..."
echo "**********************************************************************\n"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then 
    cp dot-env-example .env
fi

# Pull container images for the lab
docker pull python:3.12-slim

# Modify /etc/hosts to map the local container registry
echo Setting up cluster-registry...
sudo bash -c "echo '127.0.0.1    cluster-registry' >> /etc/hosts"

# Make git stop complaining about unsafe folders
git config --global --add safe.directory /app

echo "\n**********************************************************************"
echo "Setup complete"
echo "**********************************************************************"
