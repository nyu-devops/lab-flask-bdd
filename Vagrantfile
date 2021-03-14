# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "bento/ubuntu-20.04"
  config.vm.hostname = "ubuntu"  

  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 5984, host: 5984, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 8001, host: 8001, host_ip: "127.0.0.1"
  config.vm.network "private_network", ip: "192.168.33.10"

  # Windows users need to change the permissions explicitly so that Windows doesn't
  # set the execute bit on all of your files which messes with GitHub users on Mac and Linux
  config.vm.synced_folder "./", "/vagrant", owner: "vagrant", mount_options: ["dmode=755,fmode=644"]

  ############################################################
  # Provider for VirtualBox
  ############################################################
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 1
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  ############################################################
  # Provider for Docker
  ############################################################
  config.vm.provider :docker do |docker, override|
    override.vm.box = nil
    #docker.image = "rofrano/vagrant-provider:ubuntu"
    docker.image = "rofrano/vagrant-provider:debian"
    docker.remains_running = true
    docker.has_ssh = true
    docker.privileged = true
    docker.create_args = ["-v", "/sys/fs/cgroup:/sys/fs/cgroup:ro"]
    # docker.create_args = ["--platform=linux/arm64", "-v", "/sys/fs/cgroup:/sys/fs/cgroup:ro"]
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your ssh keys for github so that your git credentials work
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Copy your IBM Clouid API Key if you have one
  if File.exists?(File.expand_path("~/.bluemix/apiKey.json"))
    config.vm.provision "file", source: "~/.bluemix/apiKey.json", destination: "~/.bluemix/apiKey.json"
  end

  # Copy your .vimrc file so that your VI editor looks right
  if File.exists?(File.expand_path("~/.vimrc"))
    config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
  end

  ######################################################################
  # Setup a Python 3 development environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y git tree wget vim jq python3-dev python3-pip python3-venv python3-selenium
    apt-get -y autoremove

    # Install Chomium Driver
    apt-get install -y chromium-chromedriver
    
    # Create a Python3 Virtual Environment and Activate it in .profile
    sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
    sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'

    # Install app dependencies
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install wheel'
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
  SHELL

  ######################################################################
  # Add CouchDB docker container
  ######################################################################
  # docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass -v couchdb-data:/opt/couchdb/data couchdb
  config.vm.provision "docker" do |d|
    d.pull_images "couchdb"
    d.run "couchdb",
      args: "--restart=always -d --name couchdb -p 5984:5984 -v couchdb:/opt/couchdb/data -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass"
  end

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "\n************************************"
    echo " Installing IBM Cloud CLI..."
    echo "************************************\n"
    # Install IBM Cloud CLI as Vagrant user
    sudo -H -u vagrant sh -c 'curl -sL http://ibm.biz/idt-installer | bash'
    sudo -H -u vagrant sh -c 'ibmcloud config --usage-stats-collect false'
    sudo -H -u vagrant sh -c "ibmcloud cf install --version 6.46.1"
    sudo -H -u vagrant sh -c "echo 'source <(kubectl completion bash)' >> ~/.bashrc"
    sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
    echo "\n"
    echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
    echo "You can login with the following command:"
    echo "\n"
    echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apiKey.json -r us-south"
    echo "\n"
    echo "\n************************************"
    echo " For the Kubernetes Dashboard use:"
    echo " kubectl proxy --address='0.0.0.0'"
    echo "************************************\n"

    # Show the GUI URL for Couch DB
    echo "\n"
    echo "CouchDB Admin GUI can be found at:\n"
    echo "http://127.0.0.1:5984/_utils"
  SHELL

end
