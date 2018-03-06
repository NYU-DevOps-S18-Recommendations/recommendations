# Recommendations Service

[![Build Status](https://travis-ci.org/NYU-DevOps-S18-Recommendations/recommendations.svg?branch=master)](https://travis-ci.org/NYU-DevOps-S18-Recommendations/recommendations)
[![codecov](https://codecov.io/gh/NYU-DevOps-S18-Recommendations/recommendations/branch/master/graph/badge.svg)](https://codecov.io/gh/NYU-DevOps-S18-Recommendations/recommendations)

This repo contains details of our Recommendations Service.
The resource model has no persistence to keep the application simple. It's purpose is to show the correct API and return codes that should be used for a Recommendations Service API.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is to download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant VM

    $ git clone https://github.com/NYU-DevOps-S18-Recommendations/recommendations.git
    $ cd recommendations
    $ vagrant up

Once the VM is up you can use it with:

    $ vagrant ssh
    $ cd /vagrant
    $ python service.py

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

    $ exit
    $ vagrant halt

If the VM is no longer needed you can remove it with:

    $ vagrant destroy

## Manually running the Tests

Run the tests using `nosetests` and `coverage`

    $ nosetests
    $ coverage report -m --include=service.py

## What's featured in the project?

    * service.py -- the main Recommendation Service using Python Flask
    * models.py -- the data model using in-memory model
    * tests/test_service.py -- test cases against the service
    * tests/test_models.py -- test cases against the Recommendation model
