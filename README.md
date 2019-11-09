# Lab: Python Flask Behavior Driven Development

[![Build Status](https://travis-ci.org/nyu-devops/lab-flask-bdd.svg?branch=master)](https://travis-ci.org/nyu-devops/lab-flask-bdd)
[![Codecov](https://img.shields.io/codecov/c/github/nyu-devops/lab-flask-bdd.svg)]()

This repository is originally one of the labs for the *NYU DevOps* class for Spring 2017, [CSCI-GA.3033-013](http://cs.nyu.edu/courses/spring17/CSCI-GA.3033-013/) on Behavior Driven Development with Flask and Behave

The sample code is using [Flask microframework](http://flask.pocoo.org/) and is intented to test the Python support on [IBM Cloud](https://cloud.ibm.com/) environment which is based on [Cloud Foundry](https://www.cloudfoundry.org). It also uses [CouchDB](http://couchdb.apache.org) as a database for storing JSON objects.

## Introduction

One of my favorite quotes is:

_“If it's worth building, it's worth testing.
If it's not worth testing, why are you wasting your time working on it?”_

As Software Engineers we need to have the discipline to ensure that our code works as expected and continues to do so regardless of any changes, refactoring, or the introduction of new functionality.

This lab introduces Test Driven Development using `PyUnit` and `nose`. It also explores the use of using RSpec syntax with Python through the introduction of `noseOfYeti` and `expects` as plug-ins that make test cases more readable.

It also introduces Behavior Driven Development using `Behave` as a way to define Acceptance Tests that customer can understand and developers can execute!

## Setup

For easy setup, you need to have [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) installed. Then all you have to do is clone this repo and invoke vagrant:
```bash
    git clone https://github.com/nyu-devops/lab-flask-bdd.git
    cd lab-flask-bdd
    vagrant up && vagrant ssh
    cd /vagrant
```

You can now run `behave` and `nosetests` to run the BDD and TDD tests respectively.

## Manually running the Tests

These tests require the service to be running becasue unlike the the TDD unit tests that test the code locally, these BDD intagration tests are using Selenium to manipulate a web page on a running server.

Run the tests using `behave`
```shell
    $ honcho start &
    $ behave
```

Note that the `&` runs the server in the background. To stop the server, you must bring it to the foreground and then press `Ctrl+C`

Stop the server with
```shell
    $ fg
    $ <Ctrl+C>
```

Alternately you can run the server in another `shell` by opening another terminal window and using `vagrant ssh` to establish a second connection to the VM. You can also suppress all log output in the current shell with this command:

```bash
    honcho start 2>&1 > /dev/null &
```

or you can supress info logging with this command:

```bash
    gunicorn --bind 0.0.0.0 --log-level=error service:app &
```

This will suppress the normal `INFO` logging

This repo also has unit tests that you can run `nose`

```bash
    $ nosetests
```

Nose is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

## What's featured in the project?

    * ./service/service.py -- the main Service using Python Flask
    * ./service/models.py -- the data models for persistence
    * ./tests/test_service.py -- unit test cases for the server
    * ./tests/test_pets.py -- unit test cases for the model
    * ./features/pets.feature -- Behave feature file
    * ./features/steps/steps.py -- Behave step definitions

## Running these tests using Docker containers

If you want to deploy this example in a Docker container, you can run the tests from the container.

This service requires CouchDB so first start a CouchDB Docker container
```
    docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb
```

**Docker Note:**
CouchDB uses `/opt/couchdb/data` to store its data, and is exposed as a volume
e.g., to use current folder add: `-v $(pwd):/opt/couchdb/data`
You can also use Docker volumes like this: `-v couchdb:/opt/couchdb/data`

Next build this repo as a container
```bash
    docker build -t flask-bdd .
```
This will build a Docker image with the name `flask-bdd`

### nosetests
To run `nosetests` just run it in a container while linking it to the `couchdb` container that we have running by adding `--link couchdb` and `CLOUDANT_HOST=couchdb` like this.
```bash
    docker run --rm --link couchdb -e CLOUDANT_HOST=couchdb flask-bdd nosetests
```
The `--link couchdb` inserts the IP address of the `counchdb` container into the `/etc/hosts` file and then defining the environment variable `CLOUDANT_HOST=couchdb` tells our `models.py` file to use that as the name of the database server.

### Behave
To run `behave` tests we need an instance of our service running so it takes two `docker` commands, one to run our service and another to run the `behave` tests

```bash
    docker run -d --name flask-service --link couchdb -p 5000:5000 -e CLOUDANT_HOST=couchdb flask-bdd
    docker run --rm --link flask-service -e BASE_URL="http://flask-service:5000/" flask-bdd behave
```

Notice how we injected the URL of the running service into our container that is running the behave tests using an environment variable `BASE_URL` in keeping with 12-factor pratice "_III. Config:
Store config in the environment_" which recommends the passing of configuraition parameters as environment variables.

## Clean up
When you are finished exploring this lab, you can bring down these services using:

```bash
    docker stop flask-bdd
    docker stop couchdb
```
...and to remove them with:

```bash
    docker rm flask-bdd
    docker rm couchdb
```

This repository is part of the NYU class **CSCI-GA.2810-001: DevOps and Agile Methodologies** taught by John Rofrano, Adjunct Instructor, NYU Curant Institute, Graduate Division, Computer Science.
