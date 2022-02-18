# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # Chrome driver doesn't work with bento box
  # config.vm.box = "ubuntu/focal64"
  config.vm.box = "bento/ubuntu-21.04"
  config.vm.hostname = "ubuntu"

  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 5984, host: 5984, host_ip: "127.0.0.1"
  config.vm.network "private_network", ip: "192.168.56.10"

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
    # Chromium driver does not work with ubuntu so we use debian
    override.vm.hostname = "debian"
    docker.image = "rofrano/vagrant-provider:debian"
    docker.remains_running = true
    docker.has_ssh = true
    docker.privileged = true
    docker.volumes = ["/sys/fs/cgroup:/sys/fs/cgroup:rw"]
    docker.create_args = ["--cgroupns=host"]
    # Uncomment to force arm64 for testing images on Intel
    # docker.create_args = ["--cgroupns=host", "--platform=linux/arm64"] 
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
  if File.exists?(File.expand_path("~/.bluemix/apikey.json"))
    config.vm.provision "file", source: "~/.bluemix/apikey.json", destination: "~/.bluemix/apikey.json"
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

    # Install Chromium Driver
    apt-get install -y chromium-driver
    
    # Create a Python3 Virtual Environment and Activate it in .profile
    sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
    sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'

    # Install app dependencies
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip && pip install wheel'
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
  # Configure CouchDB
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "Waiting 15 seconds for CouchDB to initialize..."
    sleep 15
    echo "Creating CouchDB _users database"
    curl -i -X PUT http://admin:pass@localhost:5984/_users
  SHELL

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "\n************************************"
    echo " Installing IBM Cloud CLI..."
    echo "************************************\n"
    # WARNING!!! This only works on Intel computers
    # Install IBM Cloud CLI as Vagrant user
    ARCH=$(dpkg --print-architecture)
    if [ "$ARCH" == "amd64" ]
    then
      curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
      sudo -H -u vagrant bash -c '
          echo "alias ic=/usr/local/bin/ibmcloud" >> ~/.bash_aliases &&
          ibmcloud cf install'
    else
      echo "*** WARNING: IBM Cloud CLI does not suport your architecture :("; \
    fi

    echo "\n************************************"
    echo ""
    echo "If you have an IBM Cloud API key in ~/.bluemix/apikey.json"
    echo "You can login with the following command:"
    echo ""
    echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apikey.json -r us-south"
    echo "\nibmcloud target --cf"
    echo "\n************************************"
    # Show the GUI URL for Couch DB
    echo "\n"
    echo "CouchDB Admin GUI can be found at:\n"
    echo "http://127.0.0.1:5984/_utils"
    echo "The credentials are: userid:admin password:pass"
  SHELL

end
