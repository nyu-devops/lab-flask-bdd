# Lab: Python Flask Behavior Driven Development

[![Build Status](https://github.com/nyu-devops/lab-flask-bdd/actions/workflows/tdd-tests.yml/badge.svg)](https://github.com/nyu-devops/lab-flask-bdd/actions)
[![Build Status](https://github.com/nyu-devops/lab-flask-bdd/actions/workflows/bdd-tests.yml/badge.svg)](https://github.com/nyu-devops/lab-flask-bdd/actions)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/nyu-devops/lab-flask-bdd)

This repository is a lab from the *NYU DevOps and Agile Methodologies* graduate course [CSCI-GA.2820-001](https://cs.nyu.edu/courses/spring21/CSCI-GA.2820-001/) on Behavior Driven Development with Flask and Behave

The sample code is using [Flask microframework](http://flask.pocoo.org/) and is intended to test the Python support on [IBM Cloud](https://cloud.ibm.com/) environment which is based on [Cloud Foundry](https://www.cloudfoundry.org). It also uses [PostgreSQL](https://www.postgresql.org) as a database.

## Introduction

One of my favorite quotes is:

_“If it's worth building, it's worth testing.
If it's not worth testing, why are you wasting your time working on it?”_

As Software Engineers we need to have the discipline to ensure that our code works as expected and continues to do so regardless of any changes, refactoring, or the introduction of new functionality.

This lab introduces Test Driven Development using `PyUnit` and `nose`. It also explores the use of using RSpec syntax with Python through the introduction of the `compare` library that introduces the `expects` statement to make test cases more readable.

It also introduces Behavior Driven Development using `Behave` as a way to define Acceptance Tests that customer can understand and developers can execute!

## Prerequisite Software Installation

This lab uses Docker and Visual Studio Code with the Remote Containers extension to provide a consistent repeatable disposable development environment for all of the labs in this course.

You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

Alternately, you can use [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) to create a consistent development environment in a virtual machine (VM). 

You can read more about creating these environments in my article: [Creating Reproducable Development Environments](https://johnrofrano.medium.com/creating-reproducible-development-environments-fac8d6471f35)

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory:

```bash
$ git clone https://github.com/nyu-devops/lab-flask-bdd.git
$ cd lab-flask-bdd
```

Depending on which development environment you created, pick from the following:

### Start developing with Visual Studio Code and Docker

Open Visual Studio Code using the `code .` command. VS Code will prompt you to reopen in a container and you should say **yes**. This will take a while as it builds the Docker image and creates a container from it to develop in.

```bash
$ code .
```

Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files.

Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

## Manually running the Tests

This repository has both unit tests and integration tests. You can now run `nosetests` and `behave` to run the TDD and BDD tests respectively.

### Test Driven Development (TDD)

This repo also has unit tests that you can run `nose`

```sh
nosetests
```

Nose is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

### Behavior Driven Development (BDD)

These tests require the service to be running becasue unlike the the TDD unit tests that test the code locally, these BDD intagration tests are using Selenium to manipulate a web page on a running server.

Run the tests using `behave`

Start the server in a separate bash shell:

```sh
honcho start
```

Then start behave in your original bash shell:

```sh
behave
```

## What's featured in the project?

```text
./service/routes.py -- the main Service using Python Flask
./service/models.py -- the data models for persistence
./service/common -- a collection of status, error handlers and logging setup
./tests/test_routes.py -- unit test cases for the server
./tests/test_models.py -- unit test cases for the model
./features/pets.feature -- Behave feature file
./features/steps/web_steps.py -- Behave step definitions
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU graduate class **CSCI-GA.2810-001: DevOps and Agile Methodologies** taught by John Rofrano, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science.
