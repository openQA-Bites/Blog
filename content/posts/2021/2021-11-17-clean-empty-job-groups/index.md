---
title: Clean empty job groups in openQA
author: phoenix
type: post
date: 2021-11-17T09:51:26+01:00
categories:
  - openQA
tags:
  - openQA
  - tools
  - api
  - python
  - cli

---
In this blog post I present you a small script, which can help you to remove empty job groups from your own openQA instance. This is helpful if you have a development instance with a lot of job groups, that you never use. This script can help you to tidy the list of dangling job groups.

The script itself is a nice follow-up to my post about [Playing with the openqa API](/posts/2021-09-23-api-playing/) and consists of less than 100 lines of Python code.

* [clean-empty-jobsgroups.py](clean-empty-jobsgroups.py)

## TL;DR

* Use my [clean-empty-jobsgroups.py](clean-empty-jobsgroups.py) script to delete empty job groups from your own openQA instance
* It queries the instance for all job groups, finds the empty ones (i.e. no scheduled jobs) and will ask, if this job groups should be deleted
* The `--skip` parameter, defines (part) of the job groups names which should be ignored for deletion

Example:

    ./clean-empty-jobsgroups.py http://duck-norris.qa  --skip Maintenance,Tumbleweed
    Delete empty job group 153 'SLE 15 Virt Invidents'? [y/N] 

# Usage

```
usage: clean-empty-jobsgroups.py [-h] [-s SKIP] instance

positional arguments:
  instance              URL to the openQA instance

optional arguments:
  -h, --help            show this help message and exit
  -s SKIP, --skip SKIP  Skip job groups containing the given string in their name (comma-seprated for multiple)
```

* * *

The script requires the instance, which you want to clean, e.g. for `http://duck-norris.qa` and configured API keys for it (See subsection "openQA client API keys" below)

    ./clean-empty-jobsgroups.py http://duck-norris.qa

It fetches all job groups from the instance and then searches for the ones with no scheduled jobs in them. For each of those found empty job groups, it asks, if it should be deleted:

    ./clean-empty-jobsgroups.py http://duck-norris.qa
    ...
    Delete empty job group 153 'SLE 15 Virt Invidents'? [y/N] n
    Delete empty job group 62 'Maintenance: SLE 12 GA Updates'? [y/N] n
    Delete empty job group 38 'Maintenance: SLE 12 GA Kernel Incidents'? [y/N] n
    ...

Optionally you can also define a `--skip` parameter. If set, the script will ignore all jobs groups, which contain the given name in their job group name. For instance, if you don't want to remove any job groups with "Maintenance" or "Tumbleweed" in their name, you can do this as follows:

    ./clean-empty-jobsgroups.py http://duck-norris.qa  --skip Maintenance,Tumbleweed
    
        --skip takes a comma-separated argument, which names should be skipped for deletion

Neat! :-)

## openQA client API keys

I'm again using the [openqa-client](https://pypi.org/project/openqa-client/) python library for this tool. This is neat, because it is able to use the `/etc/openqa/client.conf` (and `~/.config/openqa/client.conf`) for using API keys.

Since we are doing `DELETE` requests, we need to have API keys for the instance under work. Make sure it is configured in one of the config files like the following template:

    # ~/.config/openqa/client.conf
    [duck-norris.qa]
    key = 0123456789ABCDEF
    secret = 0123456789ABCDEF

# Script

Here is the full [clean-empty-jobsgroups.py](clean-empty-jobsgroups.py) script:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from openqa_client.client import OpenQA_Client

class OpenQA:
	'''
	Class handling requests to OpenQA
	'''
	def __init__(self, remote : str):
		self.remote = remote
		self._client = OpenQA_Client(server=remote)
	
	def get_jobgroups(self) :
		return self._client.openqa_request(method="GET", path="job_groups")
	
	def get_jobs(self, groupid : int) :
		return self._client.openqa_request(method="GET", path="jobs/overview?groupid=%d" % (groupid))
	
	def delete_jobgroup(self, groupid: int) :
		return self._client.openqa_request(method="DELETE", path="job_groups/%d" % (groupid))

def prompt_yesno(msg, empty=None) :
	'''
	Prompt the given message and return True for a yes and False for a no anser
	'''
	while True :
		answer = input(msg).strip().lower()
		if len(answer) == 0 : 
			if empty is not None : return empty
			continue
		if answer in ['y', 'yes', 'true', '1', 'on', 'affermative', 'roger', 'okidoki'] : return True
		if answer in ['n', 'no', 'false', '0', 'off', 'negative', 'no can do', 'nope'] : return False

if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument("instance", help="URL to the openQA instance")
	parser.add_argument("-s", "--skip", help="Skip job groups containing the given string in their name (comma-seprated for multiple)")
	args = parser.parse_args()
	skip_args = [] if args.skip is None else [x.strip().lower() for x in args.skip.split(",")]
	instance = args.instance
	
	# Check if the given name should be skipped
	def skip(name) :
		name = name.strip().lower()
		for s in skip_args :
			if s in name : return True
		return False
	
	openqa = OpenQA(instance)
	for jg in openqa.get_jobgroups() : 
		_id = jg['id']
		name = jg['name']
		if skip(name) : continue
		
		jobs = openqa.get_jobs(_id)
		if len(jobs) == 0 :
			if prompt_yesno("Delete empty job group %d '%s'? [y/N] " % (_id, name), empty=False) :
				openqa.delete_jobgroup(_id)
```