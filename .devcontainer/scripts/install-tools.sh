#!/bin/bash
######################################################################
# These scripts are meant to be run in user mode as they modify
# usr settings line .bashrc and .bash_aliases
######################################################################

echo "**********************************************************************"
echo "Installing K3D Kubernetes..."
echo "**********************************************************************"
curl -s "https://raw.githubusercontent.com/rancher/k3d/main/install.sh" | sudo bash

echo "**********************************************************************"
echo "Installing IBM Cloud CLI..."
echo "**********************************************************************"
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
echo "source /usr/local/ibmcloud/autocomplete/bash_autocomplete" >> $HOME/.bashrc
# Install user mode tools
ibmcloud plugin install container-service -r 'IBM Cloud'
ibmcloud plugin install container-registry -r 'IBM Cloud'

echo "Creating aliases for new tools..."
echo "alias ic='/usr/local/bin/ibmcloud'" >> $HOME/.bash_aliases
echo "alias kc='/usr/local/bin/kubectl'" >> $HOME/.bash_aliases
echo "alias ku='/usr/local/bin/kustomize'" >> $HOME/.bash_aliases
echo "alias kns='kubectl config set-context --current --namespace'" >> $HOME/.bash_aliases

# Platform specific installs
if [ $(uname -m) == aarch64 ]; then
    echo "Installing YQ for ARM64..."
    sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm64
    sudo chmod a+x /usr/local/bin/yq
else
    echo "Installing YQ for x86_64..."
    sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
    sudo chmod a+x /usr/local/bin/yq
fi;
