# Lab: Python Flask Behavior Driven Development

[![Build Status](https://travis-ci.org/nyu-devops/lab-flask-bdd.svg?branch=master)](https://travis-ci.org/nyu-devops/lab-flask-bdd)
[![Codecov](https://img.shields.io/codecov/c/github/nyu-devops/lab-flask-bdd.svg)]()
<a href="https://zenhub.com"><img src="https://raw.githubusercontent.com/ZenHubIO/support/master/zenhub-badge.png"></a>

This repository is part of lab for the *NYU DevOps* class for Spring 2017, [CSCI-GA.3033-013](http://cs.nyu.edu/courses/spring17/CSCI-GA.3033-013/) on Behavior Driven Development with Flask and Behave

The sample code is using [Flask microframework](http://flask.pocoo.org/) and is intented to test the Python support on [IBM's Bluemix](https://bluemix.net/) environment which is based on Cloud Foundry. It also uses [Redis](https://redis.io) as a database for storing JSON objects.

## Introduction

One of my favorite quotes is:

_“If it's worth building, it's worth testing.
If it's not worth testing, why are you wasting your time working on it?”_

As Software Engineers we need to have the discipline to ensure that our code works as expected and continues to do so regardless of any changes, refactoring, or the introduction of new functionality.

This lab introduces Test Driven Development using `PyUnit` and `nose`. It also explores the use of using RSpec syntax with Python through the introduction of `noseOfYeti` and `expects` as plug-ins that make test cases more readable.

It also introduces Behavior Driven Development using `Behave` as a way to define Acceptance Tests that customer can understand and developers can execute!

## Setup

For easy setup, you need to have [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) installed. Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/nyu-devops/lab-flask-bdd.git
    cd lab-flask-bdd
    vagrant up && vagrant ssh
    cd /vagrant

You can now run `behave` and `nosetests` to run the BDD and TDD tests respectively.

## Manually running the Tests

Run the tests using `behave`

    $ behave

Run the tests using `nose`

    $ nosetests

Nose is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

## What's featured in the project?

    * ./app/server.py -- the main Service using Python Flask
    * ./tests/test_server.py -- unit test cases for the server
    * ./tests/test_pets.py -- unit test cases for the model
    * ./features/pets.feature -- Behave feature file
    * ./features/steps/steps.py -- Behave step definitions

## Running these tests using Docker containers

If you want to deploy this example in a Docker container, you can run the tests from the container.

This service requires Redis so first start a Redis container

    docker run -d --name redis-service -p 6379:6379 redis:alpine

Next build this repo as a container

    docker build -t flask-bdd .

To run `nosetests` just run it in a container while linking it to the `redis-service` container that we have running.

    docker run --rm --link redis-service flask-bdd nosetests

To run `behave` tests we need an instance of our service running so it takes two `docker` commands, one to run our service and another to run the `behave` tests

    docker run -d --name flask-service --link redis-service -p 5000:5000 flask-bdd
    docker run --rm --link flask-service -e BASE_URL="http://flask-service:5000/" flask-bdd behave

Notice how we injected the URL of the running service into our container running the behave tests using an environment variable in keeping with 12-factor configuration recommendations.

To bring down these services use:

    docker stop flask-bdd
    docker stop redis-service

...and to remove them with:

    docker rm flask-bdd
    docker rm redis-service

John Rofrano, Adjunct Professor, NYU
