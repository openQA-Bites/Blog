---
title: BCI test tutorial
author: phoenix
type: post
date: 2022-06-16T13:23:42+02:00
categories:
  - containers
tags:
  - sles
  - containers

---
Base Container Images (BCI) are a SUSE offer for a variety of container images suitable for building custom applications atop of the SUSE Linux Enterprise (SLE). They are a suitable building platform for different container applications and are available for free without subscription. In this blog post I'm covering how we test BCI before they are released and how you can run individual tests on them.

## TL;DR

Run the `bci-base` container in `podman`:

    podman run --rm -ti --name bci --hostname bci-base registry.suse.com/bci/bci-base:latest

The [BCI test suite](https://github.com/SUSE/BCI-tests) contains all BCI tests and is configured via environment variables:

    export OS_VERSION=15.3
    export TOX_PARALLEL_NO_SPINNER=1
    export CONTAINER_RUNTIME=podman
    export TARGET=obs

BCI tests are executed via `tox`

    tox -e base,init -- -n auto                 # Run base and init tests

`-k` is a useful parameter to filter or exclude test runs

    tox -e go -- -k "go_size or go_version"     # Run the go_size and the go_version functions
    
    tox -e all -- -k "not (bci/openjdk)"        # Run all tests but exclude openjdk

# What are Base Container Images?

Let's start with a quick overview from an engineering perspective. The actual product information is available at https://www.suse.com/products/base-container-images/.

BCI are small runtime containers build from SLE sources. This makes them well-tested, stable and reliable. They can be obtained for free from https://registry.suse.com/ and SUSE provides even a small update repository for a selection of packages, which should cover typical use cases for application containers (e.g. installing `vim` 😉)

BCI containers come in different flavors. There are four classical SLE containers:

* `bci/bci-base` - Container images based on SLE
* `bci/bci-minimal` - smaller SLE environment
* `bci/bci-micro` - even smaller SLE environment
* `bci/bci-init` - SLE with systemd (`podman` only)

BCI also comes as language container images in various flavors:

* `bci/golang`
* `bci/nodejs`
* `bci/openjdk`
* `bci/openjdk-devel`
* `bci/python`
* `bci/ruby`
* `bci/dotnet-runtime`
* `bci/dotnet-sdk`
* `bci/dotnet-aspnet`

Run for instance the latest `bci-base` container in `podman` with

    podman run --rm -ti registry.suse.com/bci/bci-base:latest

Or a more extended example

    podman run --rm -ti --name bci --hostname bci-base registry.suse.com/bci/bci-base:latest

# BCI tests

The BCI container build process is heavily automated and they are tested in openQA before being released. We hammer a lot of test runs on all of them before they leave the house. Thanks to Dan Čermák the tests are running using `pytest` and `tox` and are open-sourced at https://github.com/SUSE/BCI-tests in a good SUSE manner 🚀.

The different test runs are present in the [tests](https://github.com/SUSE/BCI-tests/tree/main/tests) subfolder, e.g.

* `test_base.py` - Tests the base image
* `test_go.py` - Specific tests for the `go` container
* `test_metadata.py` - Container metadata verification
* ...

This folder is a good way of getting an overview about which tests are present. Before we see how to start a specific test run, we need to first talk about the system setup. Let's start with the software requirements.

## Requirements / Installation

If you are on (open)SUSE Linux, first ensure that the necessary requirements are installed. On openSUSE the CA hanlding and PackageHub are not necessary.

```bash
# Ensure the SUSE CA is installed (SLES 15-SP3 here)
zypper -n ar --refresh http://download.suse.de/ibs/SUSE:/CA/SLE_15_SP3/SUSE:CA.repo
zypper -n in ca-certificates-suse

# Install container runtime
zypper -n in docker podman                # Pick one
systemctl enable --now docker             # If docker is used

# PackageHub
SUSEConnect -p PackageHub/15.3/x86_64

# Requirements
zypper -n --quiet in git-core python3 gcc python3-devel skopeo
pip3 --quiet install --upgrade pip
pip3 --quiet install tox --ignore-installed six

# Checkout the BCI test repository
git clone  -q --depth 1 https://github.com/SUSE/BCI-tests.git
cd BCI-tests
```

Now that you installed the requirements, let's setup the environment next.

## Configure the environment

BCI tests are configured via environment variables. Because they are running using `tox`, only the variables that are defined in `passenv` in the `tox.ini` file will be passed. All other environment variables are discarded when `tox` is invoked:

```ini
# tox.ini
...
[testenv]
...
passenv =
    CONTAINER_RUNTIME
    HOME
    USER
    XDG_CONFIG_HOME
    XDG_RUNTIME_DIR
    BCI_DEVEL_REPO
    OS_VERSION
    OS_PRETTY_NAME
    BASEURL
    TARGET
```

The following environment variables are being used currently:

| Variable | Description |
|----------|-------------|
| `OS_VERSION` | Set the BCI container version under test |
| `CONTAINER_RUNTIME` | Container runtime to be used (`podman` or `docker`) |
| `TARGET` | Where to fetch the BCI container from. Can be `obs`, `ibs` or `ibs-cr` |
| `BASEURL` | Custom URL to fetch the BCI images from, if `TARGET` is not set |
| `BCI_DEVEL_REPO` | Define the update repository within the container |
| `TOX_PARALLEL_NO_SPINNER` | If set to `1` then no spinner will be displayed |

The `TARGET` variable defines where the BCI container should be pulled from. `obs` sets the source to registry.opensuse.org, `ibs` to registry.suse.de and `ibs-cr` to the testing repository within `ibs` ("internal build service").

## How to run a specific test

In the most basic example we just run the `base` test:

    tox -e base

Now, let's run two tests (`base` and `init`):

    tox -e base,init -- -n auto
    
    # Arguments after -- are passed to pytest, so `-n auto` tells pytest to enable multi-threading

## Filter a test run

Use the `-k` parameter to exclude or specify which tests should be running. This parameter is passed to `pytest`, so it needs to be added after two dashes `--`.

### Example: Filter for ruby tests

To run all test runs but filter them by the name of the container, you can do

    tox -e all -- -k "bci/ruby_2.5"

### Example: Exclude openjdk

I want to run all tests except openjdp

    tox -e all -- -k "not (bci/openjdk)"

### Example: Run one specific test function

To only run the `test_go_size` function from `tests/test_go.py` you can also pass a function name without the `test_` prefix:

    tox -e go -- -k "go_size"

Of course you can combine more functions

    tox -e go -- -k "go_size or go_version"

## Run a specific SLE version

Use the `OS_VERSION` variable to tell BCI test which container version should be tested:

    OS_VERSION=15.3 tox -e all

## Select source for the BCI images under test

    TARGET=ibs tox -e all                # Use the images from the internal build service
    TARGET=ibs-cr tox -e all             # Use the images under test
    TARGET=obs tox -e all                # Use the images from open build service

* * *

And that's a short summary on how you can use our BCI test on your local machine or within a VM.
