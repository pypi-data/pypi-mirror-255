Burlap - configuration management designed for simplicity and speed
===================================================================

[![](https://img.shields.io/pypi/v/burlap.svg)](https://pypi.python.org/pypi/burlap)
[![Pipeline Status](https://gitlab.com/chrisspen/burlap/badges/master/pipeline.svg)](https://gitlab.com/chrisspen/burlap/commits/master) 
[![](https://pyup.io/repos/gitlab/chrisspen/burlap/shield.svg)](https://pyup.io/repos/gitlab/chrisspen/burlap)

Overview
--------

Burlap is a [configuration management](https://en.wikipedia.org/wiki/Comparison_of_open-source_configuration_management_software)
tool and framework for deploying software to servers.

It's written in Python and is built ontop of [Fabric](http://www.fabfile.org/) to run commands remotely over SSH.

Unlike [Chef](https://www.chef.io/) or [Ansible](http://www.ansible.com/) that target large "web-scale" platforms at the expense of great complexity, Burlap targets small- to medium-scale platforms and keeps its configuration simple.

Much of the code is also heavily influenced by [Fabtools](https://github.com/fabtools/fabtools), another Fabric-based toolkit.

Python 2.7 is supported through version 0.9.54.

Installation
------------

Install the package via pip with:

    pip install burlap

To use the `boto` package for AWS support, install with `pip install burlap[aws]`.

Quickstart & Usage
------------------

Basic call format:

    fab <role> <task>

A task is a Fabric command which can perform an arbitrary operation.

A role is a special type of task that defines the servers that the following tasks should apply to.

A role is defined in a top-level directory called 'roles', where every sub-directory represents the name of a role.

The file `settings.yaml` inside this directory defines all the settings for this role.

To create a base Burlap skeleton project with sample roles, run `burlap-admin.py skel myproject`.

There can be an arbitrary number of tasks called:

    fab staging rabbitmq.configure cron.configure apache.configure service.post_deploy

Tasks are organized in classes called Satchels. This allows them to share state and have a more organized naming scheme.

For example, all the tasks relating to Apache are in the Apache satchel, so to stop, deploy your Apache configuration, and then restart the staging server, you would do:

    fab staging apache.stop apache.configure apache.restart

However, it gets even simpler than this. If you add `apache` to the `services` list inside `roles/staging/settings.yaml`, then Burlap will track changes and automatically deploy them when you run:

    fab staging deploy.push

Each satchel defines how its changes are tracked, which are reported in the form of a manifest.

Burlap retrieves this manifest for each satchel before and after the deployment, and calculates the difference to determine which satchels have outstanding changes with need to be deployed.

Satchels can define dependencies, telling Burlap to run certain tasks in a specific order.

For example, a Django project hosted on Apache would require the Apache configuration to be deployed before any Django project code.

This allows a role to contain an arbitrary number of satchels, whose deployment can be calculated automatically.

However, this auto-deployer can't foresee all use cases, and should exceptions arise, you can reset Burlap's last manifest, implicitly telling it that, "Everything that needs to be deployed has been deployed", but running:

    fab <role> deploy.fake

Virtually all Burlap tasks support a `dryrun` parameter, which, when set, will only output the command without applying any substantial changes to the server. It's activated like:

    fab <role> some_task:dryrun=1

Most Burlap tasks also support a `verbose` parameter, which will activate additional debugging info as defined by each satchel. It's activated like:

    fab <role> some_task:verbose=1

Nearly all of Burlap's built-in tasks run Bash commands behind the scenes. Therefore, by activating dryrun mode and hiding all superfluous output except the generated Bash commands,
it's possible to convert a Burlap call to a Bash script. To do this, set the environment variable `BURLAP_COMMAND_PREFIX=0`, activate dryrun, and capture the output to a file. e.g.

    BURLAP_COMMAND_PREFIX=0 BURLAP_SHELL_PREFIX=1 fab staging some_task:dryrun=1 > myscript.sh

To run all tests:

    tox -c tox-full.ini
    
To run all tests on a specific environment:

    tox -c tox-full.ini -e py312-ubuntu_22_04_64

To run a specific test in a specific environment:

    tox -c tox-full.ini -e py312-ubuntu_22_04_64 -- -s <path_to_file>::<TestCaseName>::<test_name>

e.g.

    tox -c tox-full.ini -e py312-ubuntu_22_04_64 -- -s burlap/tests/test_apache.py::ApacheTests::test_diff
