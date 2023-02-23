#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
from openqa_client.client import OpenQA_Client


def get_schedule(instance, job):
    """
    Build a SCHEDULE parameter from the given job (id) on the given instance
    """
    schedule = []

    ## Configure instance
    client = OpenQA_Client(server=instance)
    path = "jobs/%d/details" % (job)
    job = client.openqa_request(method="GET", path=path)["job"]
    # iterate over testresults. category is only set for a new category (e.g. "installation", "console", ecc.)
    category = ""
    for result in job["testresults"]:
        if "category" in result:
            category = result["category"]
        name = result["name"]
        schedule.append("%s/%s" % (category, name))
    return schedule


def is_int(x):
    try:
        x = int(x)
        return True
    except ValueError:
        return False


def print_schedule(schedule):
    # add 'tests/' as prefix
    schedule = map(lambda x: "tests/" + x, schedule)
    text = ",".join(schedule)
    print("SCHEDULE=%s" % text)


"""
Cleans an url, i.e. remove a possible fragment
"""


def clean_url(url):
    i = url.find("#")
    if i > 0:
        return url[:i]
    return url


def print_usage():
    prog = sys.argv[0]
    print("Usage: %s [INSTANCE,JOBURL,JOBID]" % prog)
    print("  Assemble the SCHEDULE= variable from a given openQA job")
    print("")
    print("Examples:")
    print("  %s https://openqa.opensuse.org/tests/12345" % prog)
    print("  %s https://openqa.opensuse.org/t12345" % prog)
    print(
        "  %s --ooo 12345                                          # Same as above"
        % prog
    )
    print(
        "  %s --o3 12345                                           # Same as above"
        % prog
    )
    print(
        "  %s --osd 12345                                          # Use openqa.suse.de"
        % prog
    )
    print(
        "  %s https://openqa.opensuse.org 12345 67890              # Two jobs, first define the instance"
        % prog
    )
    print("  %s https://openqa.opensuse.org/tests/12345 67890        # Two jobs" % prog)


if __name__ == "__main__":
    instance = "https://openqa.opensuse.org"  # Default instance

    # Lazy argument matching because I'm lazy.
    for url in sys.argv[1:]:
        url = clean_url(url)
        if url == "-h" or url == "--help":
            print_usage()
            sys.exit(0)
        elif url == "--osd":
            instance = "https://openqa.suse.de"
        elif url == "--ooo" or url == "--o3":
            instance = "https://openqa.opensuse.org"
        elif "/tests/" in url:  # https://openqa.opensuse.org/tests/12345
            i = url.find("/tests/")
            instance = url[:i]
            job = int(url[i + 7 :])
            schedule = get_schedule(instance, job)
            print_schedule(schedule)
        elif "/t" in url:  # https://openqa.opensuse.org/t12345
            i = url.rfind("/t")
            instance = url[:i]
            job = int(url[i + 2 :])
            schedule = get_schedule(instance, job)
            print_schedule(schedule)
        elif url.startswith("http://") or url.startswith("https://"):
            # Assume it's an instance
            instance = url
        elif is_int(
            url
        ):  # after an instance is defined we can also just pass the job id
            job = int(url)
            schedule = get_schedule(instance, job)
            print_schedule(schedule)
        else:
            sys.stderr.write("Invalid argument: %s\n" % url)
            sys.exit(1)
