---
title: Reviewing openQA jobs with openqa-revtui
author: phoenix
type: post
date: 2023-01-27T09:12:16+01:00
categories:
  - openqa
  - tools
tags:
  - openqa
  - tools
  - cli

---
The `openqa-revtui` tool is a neat CLI utility for helping you review openQA jobs and job groups.
It is part of the `openqa-mon` project, which has grown in the last years and now consists on more than the job monitoring tool itself.

In comparison to the already powerful WebUI, this tool presents the jobs that require attention continuously in a terminal. It can even notify you about failing jobs right when they appear.

## TL;DR

* `openqa-revtui` is a tool for monitoring job groups from your terminal
* See the screenshots below.
* Installation on Tumbleweed: `zypper in openqa-mon`
* The tool is configured via customizable `toml` files
* Example configuration files are available in [_review](https://github.com/grisu48/openqa-mon/tree/master/_review) folder of the project

Usage: e.g. to monitor the jobs from the `opensuse-tumbleweed.toml` [file](https://github.com/grisu48/openqa-mon/blob/master/_review/opensuse-tumbleweed.toml)

```
openqa-revtui -c opensuse-tumbleweed.toml
```

* Cave: The tool might hang itself once in a while (See [issue 56](https://github.com/grisu48/openqa-mon/issues/56)) - don't run it unattended
* Cave: Don't rely on this tool as your only means of reviewing jobs

To get notified about job status updates, you can use the `-n` program parameter.

# openQA job review in your terminal

`openqa-revtui` shows a configurable list of jobs and filters for the ones that require attention. In practice it displays the failing and incomplete jobs of multiple job groups in one convenient place in the terminal.

Let's talk pictures! This is an example screenshot showing all jobs that need to be reviewed for SLE Micro:

![Screenshot of SLE Micro jobs that need to be reviewed because they are failing or incomplete](openqa-revtui1.png)


The tool can be interacted with, e.g. to show all jobs instead of the ones that require attention. Here is the same job list but by pressing `h` you can show/hide all jobs.

![All Jobs for SLE Micro, also the passing and softfailing ones](openqa-revtui2.png)

You can see, that the tool tried to hide all jobs that not interesting for a reviewer and tried to focus on the ones that require attention. The user can configure, which jobs to display and which ones to hide.

## What??!?

Ok, that was too fast. Let me show you how this works in practice. The GIF is 1 minute long and it shows the following:

* You can feed a customizable `toml` file to the tool. This makes it versatile
* Given that configuration yaml, the tool will fetch all jobs in the defined job groups
* You can toggle between the jobs that need review (failed ones) and the full job list
* You can scroll the job list with the arrows and the page up-down keys
* You can switch between sorting mechanisms (by group or all jobs in one list)

[![Demonstration of the tool in action](demo.gif)](demo.gif)

## How can I use this tool?

### Installation

The tool ships with the `openqa-mon` package in Tumbleweed. If you are on Leap, you can use my [tools repository on OBS](https://build.opensuse.org/project/show/home:ph03nix:tools). On any other Linux platforms, I do build statically linked binaries for every new [release of openqa-mon](https://github.com/grisu48/openqa-mon/releases), however the project should be very easy to build on your own machine. [Build instructions](https://github.com/grisu48/openqa-mon#building) are on the project page.

On Tumbleweed, life is easy:

    zypper in openqa-mon

Sip on your coffee, and enjoy.

### Usage

```
$ openqa-revtui -h
Usage: openqa-revtui [OPTIONS] [FLAVORS]

OPTIONS
    -h,--help                           Print this help message
    -c,--config FILE                    Load toml configuration from FILE
    -r,--remote REMOTE                  Define openQA remote URL (e.g. 'https://openqa.opensuse.org')
    -q,--rabbit,--rabbitmq URL          Define RabbitMQ URL (e.g. 'amqps://opensuse:opensuse@rabbit.opensuse.org')
    -i,--hide,--hide-status STATUSES    Comma-separates list of job statuses which should be ignored
    -p,--param NAME=VALUE               Set a default parameter (e.g. "distri=opensuse")
    -n,--notify                         Enable notifications
    -m,--mute                           Disable notifications

```

In short, just throw a configuration file at it, and you're good to go:

```
$ openqa-revtui -c opensuse-tumbleweed.toml
```

### Configuration

The tool is configured via customizable `toml` files. Example files are provided in the [_review](https://github.com/grisu48/openqa-mon/tree/master/_review) folder of the project.

The `toml` configuration file consists of a global configuration section where you define the instance and how the program should behave, and the job groups you want to monitor. Let's take the current configuration file for Tumbleweed as example:

```toml
# Instance configuration
Instance = "https://openqa.opensuse.org"
RabbitMQ = "amqps://opensuse:opensuse@rabbit.opensuse.org"
RabbitMQTopic = "opensuse.openqa.job.done"

# Program behaviour
HideStatus = [ "scheduled","passed","assigned","running","softfailed","reviewed" ]
RefreshInterval = 60
MaxJobs = 20
GroupBy = "groups"
DefaultParams = { distri="opensuse", version = "Tumbleweed" }


## Define job groups

[[Groups]]
Name = "openSUSE Tumbleweed DVD"
Params = { flavor = "DVD" }
MaxLifetime = 86400

[[Groups]]
Name = "openSUSE Tumbleweed Network"
Params = { flavor = "NET" }
MaxLifetime = 86400

[[Groups]]
Name = "openSUSE Tumbleweed JeOS"
Params = { flavor = "JeOS-for-kvm-and-xen" }
MaxLifetime = 86400

[[Groups]]
Name = "openSUSE Tumbleweed Gnome-Live"
Params = { flavor = "GNOME-Live" }
MaxLifetime = 86400
[[Groups]]
Name = "openSUSE Tumbleweed KDE-Live"
Params = { flavor = "KDE-Live" }
MaxLifetime = 86400
```

You can see, that first we define the openQA instance by URL and RabbitMQ parameters. The tool listens on RabbitMQ for immediate job status updates, but also periodically polls all jobs to be sure to not have missed any update. 

* `RefreshInterval` defines the number of seconds between job polling updates

* `MaxJobs` limits the number of jobs per group to display to avoid unnecessary spamming.

* `GroupBy = groups` defines the display method. This is the only one that currently makes sense.

The previous settings are the boring ones that I typically just copy&paste. Select a matching example file and you're good. Those rarely need adjustment. So let's now go to the more interesting settings:

* `HideStatus` defines a list of job statuses, which are going to be **hidden**. This is where you can configure, which jobs to display and which ones to hide. Mind the special status `reviewed`. Those are failed jobs that contain at least one reference to a Bugzilla or progress ticket. I added this to make your life easier 😃

* `DefaultParams` defines some parameter that will be applied to all `Groups` definitions. This is useful to avoid repetition of parameters that do not change over the groups. Here e.g. we want to display always the results for Tumbleweed defined by its `distri` and `version` parameter.

* The `[[Groups]]` sections define the Job groups that are displayed. Each of those section gets a custom `Name`, which is displayed in the tool and customizable `Params`, which are the query parameter for openQA. We will see in a second what this means. Another useful parameter here is `MaxLifetime` that defines the maximum age of jobs in seconds. Older jobs will be discarded.

### How does the tool work?

The tool first fetches an overview of all defined job groups, using the parameters from the configuration `toml` file. It then continuously scans for status updates on those jobs.

First we obtain a list of all currently running jobs via a openQA REST API call.
openQA provides conveniently a overview in `/api/v1/jobs/overview`. This endpoint accepts parameters like `distri`, `version`, `build`, ... and is used to fetch an overview of the currently running jobs. The parameters defined in `Params` and `DefaultParams` are exactly the parameters that get passed to this REST API call. This is how you can configure, which jobs `openqa-revtui` will display.

Example of valid calls are e.g.

* https://openqa.opensuse.org/api/v1/jobs/overview?distri=microos
* https://openqa.opensuse.org/api/v1/jobs/overview?distri=opensuse&version=Tumbleweed&flavor=DVD

Once the job list is obtained, the tool listens on RabbitMQ for job status updates. In addition once in a while manually polls all jobs in the list are done to be sure to remain in sync.

## Caveats 💥

Two caveats apply.

First: There is still an [annoying bug present](https://github.com/grisu48/openqa-mon/issues/56) that the tool hangs itself once in a while and starts to consume a full CPU core. This happens sporadically and I haven't been able to pinpoint the issue (yet). So don't run this tool unattended over lunch or something. 🔥

While the tool itself should work fine, don't rely on it as single source of truth. There are situations, when it does not find all jobs. If you're on review shift, this is fine to cover 99% of all jobs, but always do at least one manual round to ensure, that no jobs have been forgotten.

***

And that's it! The tool can be easily installed on Tumbleweed, and by looking at the provided example files in the [_review](https://github.com/grisu48/openqa-mon/tree/master/_review) folder, you should be able to create your own template file for reviewing openQA jobs in the CLI.

More power to you! 🚀
