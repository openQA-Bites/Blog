#!/usr/bin/python3
# -*- coding: utf-8 -*-
# openQA tools workshop - API example
# Note: For a overview of the available http routes/methods visit
# https://openqa.opensuse.org/api/v1

import requests
import json

## Terminal color codes
class TColor:
    """ see https://en.wikipedia.org/wiki/ANSI_escape_code#Colors """

    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BRIGHTYELLOW = "\u001b[93m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"
    RESET = "\u001b[0m"

    @staticmethod
    def colorState(state: str):
        """
        Return the color of a openQA job state
        """
        if state == "running":
            return TColor.BLUE
        elif state == "assigned":
            return TColor.CYAN
        elif state == "scheduled":
            return TColor.CYAN
        elif state == "failed":
            return TColor.RED
        elif state == "softfailed":
            return TColor.YELLOW
        elif state == "failed-ignored":
            return TColor.BRIGHTYELLOW
        elif state == "passed":
            return TColor.GREEN
        else:
            return TColor.WHITE


class Comment:
    """
    Comment fetched from openQA
    """

    def __init__(self, js=None):
        # get a value if existing
        def getval(name, default=None):
            if js is None:
                return default
            if name in js:
                return js[name]
            return default

        self.bugrefs = getval("bugrefs", [])
        self.created = getval("created", "")
        self.id = getval("id", "")
        self.renderedMarkdown = getval("renderedMarkdown", "")
        self.text = getval("text", "")
        self.updated = getval("updated", "")
        self.userName = getval("userName", "")

    def isIgnore(self):
        """
        Checks if this comment marks to ignore a failure
        """
        return "@ttm ignore" in self.text

    def __str__(self):
        return self.text


def api_fetch(url: str):
    """
    Fetch the json from the given url. Raises an HTTPError on http errors
    """
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    distri = "opensuse"
    version = "15.3"  # Leap 15.3
    build = "9.220"  # Current build, could be passed as command line argument
    job_group = (
        77  # Leap 15.3 Images - See https://openqa.opensuse.org/group_overview/77
    )

    url = (
        "https://openqa.opensuse.org/api/v1/jobs/overview?distri=%s&version=%s&build=%s&groupid=%d"
        % (distri, version, build, job_group)
    )
    c_group = api_fetch(url)
    # print(json.dumps(c_group))

    # Python list comprehension: https://www.python.org/dev/peps/pep-0202/
    job_ids = [job["id"] for job in c_group]
    jobs = [
        api_fetch("https://openqa.opensuse.org/api/v1/jobs/%d" % i) for i in job_ids
    ]
    for job in jobs:
        job = job["job"]
        # print(json.dumps(job))
        jobid = job["id"]

        name = job["name"]
        state = job["state"]
        if state == "done":
            state = job["result"]

        # If the test is failed, also check comments for some hints
        if state == "failed":
            comments = api_fetch(
                "https://openqa.opensuse.org/api/v1/jobs/%d/comments" % jobid
            )
            comments = [Comment(x) for x in comments]
            for comment in comments:
                if comment.isIgnore():
                    state = "failed-ignored"

        color = TColor.colorState(state)
        print("%s%-100s\t%-20s%s" % (color, name, state, TColor.RESET))
