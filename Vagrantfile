# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.define "bdd" do |bdd|
      bdd.vm.box = "ubuntu/xenial64"
      # set up network ip and port forwarding
      bdd.vm.network "forwarded_port", guest: 5000, host: 4617, host_ip: "127.0.0.1"
      bdd.vm.network "private_network", ip: "192.168.33.10"

      # Windows users need to change the permissions explicitly so that Windows doesn't
      # set the execute bit on all of your files which messes with GitHub users on Mac and Linux
      bdd.vm.synced_folder "./", "/vagrant", owner: "ubuntu", mount_options: ["dmode=755,fmode=644"]

      bdd.vm.provider "virtualbox" do |vb|
        # Customize the amount of memory on the VM:
        vb.memory = "512"
        vb.cpus = 1
        # Fixes some DNS issues on some networks
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
        vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
      end
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your private ssh keys to use with github
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  ######################################################################
  # Setup a Python development environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    #apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y
    apt-get update
    apt-get install -y wget git zip tree python-pip python-dev
    apt-get -y autoremove
    pip install --upgrade pip
    # Make vi look nice
    sudo -H -u ubuntu echo "colorscheme desert" > ~/.vimrc
    echo "\n****************************"
    echo " Installing the Bluemix CLI"
    echo "****************************\n"
    wget https://clis.ng.bluemix.net/download/bluemix-cli/latest/linux64
    tar -zxvf linux64
    cd Bluemix_CLI/
    ./install_bluemix_cli
    cd ..
    rm -fr Bluemix_CLI/
    rm linux64
    # Install PhantomJS for Selenium browser support
    echo "\n***********************************"
    echo " Installing PhantomJS for Selenium"
    echo "***********************************\n"
    sudo apt-get install -y chrpath libssl-dev libxft-dev
    # PhantomJS https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    cd ~
    export PHANTOM_JS="phantomjs-1.9.7-linux-x86_64"
    #export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
    wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
    sudo tar xvjf $PHANTOM_JS.tar.bz2
    sudo mv $PHANTOM_JS /usr/local/share
    sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
    rm -f $PHANTOM_JS.tar.bz2
    # Install app dependencies
    echo "\n******************************"
    echo " Installing app dependencies"
    echo "******************************\n"
    cd /vagrant
    sudo pip install -r requirements.txt
  SHELL

  ######################################################################
  # Add Redis docker container
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Prepare Redis data share
    sudo mkdir -p /var/lib/redis/data
    sudo chown ubuntu:ubuntu /var/lib/redis/data
  SHELL

  # Add Redis docker container
  config.vm.provision "docker" do |d|
    d.pull_images "redis:alpine"
    d.run "redis:alpine",
      args: "--restart=always -d --name redis -h redis -p 6379:6379 -v /var/lib/redis/data:/data"
  end

end
