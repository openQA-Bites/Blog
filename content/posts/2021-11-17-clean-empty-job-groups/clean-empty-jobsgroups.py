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
