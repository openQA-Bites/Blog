---
title: Extract SCHEDULE from an openQA job
author: phoenix
type: post
date: 2021-12-13T13:46:51+01:00
categories:
  - openQA
tags:
  - openQA
  - Python
  - tools

---
Then using `openqa-clone-job` (and derivates) one can use the `SCHEDULE` variable to clone a test run with a custom set of test modules. This is particular useful, when developing a new test case and you need a verification run with e.g. one additional test module or excluding some failing ones.
However it is sometimes cumbersome to type out a neverending of tests into a custom `SCHEDULE` variable, if the amount of test modules exceeds 5 or more tests (e.g. [extra_tests_textmode](https://openqa.opensuse.org/tests/2082504) - good luck!).


## TL'DR

* The [openqa-extract-schedule](openqa-extract-schedule.py) script takes the link to an openQA job and extracts the `SCHEDULE` variable for you
* This variable can be used with `openqa-clone-job` (and derivatives)
* It's hacky, but it works

This is how it works:

    $ openqa-extract-schedule https://openqa.opensuse.org/tests/2083138
    SCHEDULE=tests/installation/bootloader_uefi,tests/jeos/firstrun,tests/jeos/record_machine_id,tests/console/force_scheduled_tasks,tests/jeos/grub2_gfxmode,tests/jeos/diskusage,tests/jeos/build_key,tests/console/prjconf_excluded_rpms,tests/console/journal_check,tests/microos/libzypp_config,tests/update/zypper_clear_repos,tests/console/zypper_ar,tests/console/zypper_ref,tests/containers/podman_image,tests/containers/docker_image,tests/containers/container_diff,tests/console/coredump_collect

The full script is at the end of this post.

# The problem

Today when working on the schedule of the JeOS container test runs on Tumbleweed ([openqa.opensuse.org/t2083138](https://openqa.opensuse.org/tests/2083138)) I faced this problem. One can easily see that the resulting list is prone to human typing errors and it is become annoyingly large to even start with:

    tests/installation/bootloader_uefi
	tests/jeos/firstrun
	tests/jeos/record_machine_id
	tests/console/force_scheduled_tasks
	tests/jeos/grub2_gfxmode
	tests/jeos/diskusage
	tests/jeos/build_key
	tests/console/prjconf_excluded_rpms
	tests/console/journal_check
	tests/microos/libzypp_config
	tests/update/zypper_clear_repos
	tests/console/zypper_ar
	tests/console/zypper_ref
	tests/containers/podman_image
	tests/containers/docker_image
	tests/containers/container_diff
	tests/console/coredump_collect

If there would only be a way to making this task a bit easier for me ...


# Automate it!

So, after half a minute of typing and realizing that this is a very stupid task to do, I figured, "what the heck, let's automate this". So I hacked my [openqa-extract-schedule](openqa-extract-schedule.py) python script which does exactly this task. You give it a link to an openQA job and it assembled the `SCHEDULE` variable for `openqa-clone-job` for you:


    $ openqa-extract-schedule https://openqa.opensuse.org/tests/2083138
    SCHEDULE=tests/installation/bootloader_uefi,tests/jeos/firstrun,tests/jeos/record_machine_id,tests/console/force_scheduled_tasks,tests/jeos/grub2_gfxmode,tests/jeos/diskusage,tests/jeos/build_key,tests/console/prjconf_excluded_rpms,tests/console/journal_check,tests/microos/libzypp_config,tests/update/zypper_clear_repos,tests/console/zypper_ar,tests/console/zypper_ref,tests/containers/podman_image,tests/containers/docker_image,tests/containers/container_diff,tests/console/coredump_collect

The script comes with a help message (`-h` or `--help`), which gives you some examples that should point you in the right direction ...

    openqa-extract-schedule -h
    Usage: /home/phoenix/bin/openqa-extract-schedule [INSTANCE,JOBURL,JOBID]
      Assemble the SCHEDULE= variable from a given openQA job

    Examples:
      /home/phoenix/bin/openqa-extract-schedule https://openqa.opensuse.org/tests/12345
      /home/phoenix/bin/openqa-extract-schedule https://openqa.opensuse.org/t12345
      /home/phoenix/bin/openqa-extract-schedule --ooo 12345                                          # Same as above
      /home/phoenix/bin/openqa-extract-schedule --o3 12345                                           # Same as above
      /home/phoenix/bin/openqa-extract-schedule --osd 12345                                          # Use openqa.suse.de
      /home/phoenix/bin/openqa-extract-schedule https://openqa.opensuse.org 12345 67890              # Two jobs, first define the instance
      /home/phoenix/bin/openqa-extract-schedule https://openqa.opensuse.org/tests/12345 67890        # Two jobs

# Script

And here is the full script [openqa-extract-schedule](openqa-extract-schedule.py)

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
from openqa_client.client import OpenQA_Client

def get_schedule(instance, job) :
	'''
	Build a SCHEDULE parameter from the given job (id) on the given instance
	'''
	schedule = []
	
	## Configure instance
	client = OpenQA_Client(server=instance)
	path = "jobs/%d/details" % (job)
	job = client.openqa_request(method="GET", path=path)['job']
	# iterate over testresults. category is only set for a new category (e.g. "installation", "console", ecc.)
	category = ""
	for result in job['testresults'] :
		if "category" in result : category = result['category']
		name = result['name']
		schedule.append("%s/%s" % (category, name))
	return schedule

def is_int(x) :
	try :
		x = int(x)
		return True
	except ValueError :
		return False

def print_schedule(schedule) :
	# add 'tests/' as prefix
	schedule = map(lambda x : 'tests/' + x, schedule)
	text = ",".join(schedule)
	print("SCHEDULE=%s" % text)

'''
Cleans an url, i.e. remove a possible fragment
'''
def clean_url(url) :
	i = url.find('#')
	if i > 0 : return url[:i]
	return url

def print_usage() :
	prog = sys.argv[0]
	print("Usage: %s [INSTANCE,JOBURL,JOBID]" % prog)
	print("  Assemble the SCHEDULE= variable from a given openQA job")
	print("")
	print("Examples:")
	print("  %s https://openqa.opensuse.org/tests/12345" % prog)
	print("  %s https://openqa.opensuse.org/t12345" % prog)
	print("  %s --ooo 12345                                          # Same as above" % prog)
	print("  %s --o3 12345                                           # Same as above" % prog)
	print("  %s --osd 12345                                          # Use openqa.suse.de" % prog)
	print("  %s https://openqa.opensuse.org 12345 67890              # Two jobs, first define the instance" % prog)
	print("  %s https://openqa.opensuse.org/tests/12345 67890        # Two jobs" % prog)

if __name__ == "__main__":
	instance = "https://openqa.opensuse.org"         # Default instance
	
	# Lazy argument matching because I'm lazy.
	for url in sys.argv[1:] :
		url = clean_url(url)
		if url == "-h" or url == "--help" :
			print_usage()
			sys.exit(0)
		elif url == "--osd" :
			instance = "https://openqa.suse.de"
		elif url == "--ooo" or url == "--o3" :
			instance = "https://openqa.opensuse.org"
		elif "/tests/" in url :         # https://openqa.opensuse.org/tests/12345
			i = url.find("/tests/")
			instance = url[:i]
			job = int(url[i+7:])
			schedule = get_schedule(instance, job)
			print_schedule(schedule)
		elif "/t" in url :              # https://openqa.opensuse.org/t12345
			i = url.rfind("/t")
			instance = url[:i]
			job = int(url[i+2:])
			schedule = get_schedule(instance, job)
			print_schedule(schedule)
		elif url.startswith("http://") or url.startswith("https://") :
			# Assume it's an instance
			instance = url
		elif is_int(url) :              # after an instance is defined we can also just pass the job id
			job = int(url)
			schedule = get_schedule(instance, job)
			print_schedule(schedule)
		else :
			sys.stderr.write("Invalid argument: %s\n" % url)
			sys.exit(1)
```