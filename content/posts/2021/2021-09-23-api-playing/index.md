---
title: Playing with the openqa API
author: phoenix
type: post
date: 2021-09-24T08:00:00+02:00
categories:
  - openqa
tags:
  - openqa
  - api
  - scripting
  - python

---
Today we are going to play a bit around with the amazing API that every openQA instance provides.
The aim of this tutorial is to show how the API can be accessed using a simple language like python.
More advanced topics like job posting, deletion and other methods that require authentication are possible but not covered extensively in this post.
The reference for this post will be [openqa.opensuse.org](https://openqa.opensuse.org), but everything works pretty much with every openQA instance.

Downloadable files:

* Exercise 1: [overview_leap_images.py](overview_leap_images.py)
* Exercise 2: [client_example.py](client_example.py) (requires [openqa_client](https://pypi.org/project/openqa-client/))

Both example files should work as stand-alone without any prior configuration (especially no API keys required).

**[2021-09-27] Update**: The [workshop video](https://www.youtube.com/watch?v=RUVtn6unMfs) is now online as well.

## Exercise 1: Simple job overview program

The first thing is that we want to query the job status of a certain job group and display all jobs on the terminal. Because colors are cool, we color-code each job line according to the status. For this exercise we are going to display the latest [openSUSE Leap 15.3 Images](https://openqa.opensuse.org/group_overview/77) test runs.

![Screenshot of the finished program showing an overview of different jobs. Each job is in one line with it's name and status (e.g. failed, passed, scheduled). Each line is colored depending on the job status - passed green, softfailed yellow, failed ones are red. There is one job colored bright yellow with the state "failed-ignored"](example-overview.png)

My first contact point with the openQA API is the listing of routes on the 404 page, e.g. on [https://openqa.opensuse.org/api/v1](https://openqa.opensuse.org/api/v1). Everything below `/api/v1` is interesting. openQA offers a lot of paths and methods to be accessed. The provided API makes openQA an incredibly useful tool for various monitoring and automation tools, e.g. [openqa-mon](https://github.com/grisu48/openqa-mon), a CLI monitoring utility.

Most (if not all) results are being returned as `json` objects, thus any modern programming language should not have any problems to process it. For error checking the http status codes are accurate and enough for most cases.

For this example we take the latest [openSUSE Leap 15.3 Images](https://openqa.opensuse.org/group_overview/77) test runs. Those can be found on [openqa.opensuse.org](https://openqa.opensuse.org) -> Job Groups -> `openSUSE Leap 15.3 Images` (Job Group 77). For this exercise we also use the hardcoded current build `9.220`. A possible improvement could be to fetch the latest build or pass it as program argument, this is however left to the interested user and beyond the scope of this simple exercise.

Today, the latest build from [openSUSE Leap 15.3 Images](https://openqa.opensuse.org/group_overview/77) is the following

    https://openqa.opensuse.org/tests/overview?distri=opensuse&version=15.3&build=9.220&groupid=77

This link reveals a lot of useful parameters already: `distri=opensuse`, `version=15.3`, `build=9.220`, `groupid=77`. Those we will need when crafting our request to the API. Feel free to adjust those values to your needs or add additional ones.

Ok, with this link and the given parameters we have everything we need to write our little project ([overview_leap_images.py](overview_leap_images.py)):

```python
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
```

*I wanted to write this tutorial script in less than 100 lines of code, which I achieved before running `black` on it. I blame the code formatter for over-shooting a little bit ;-)*

Ok, let's walk through this. We first fetch the job overview from
[https://openqa.opensuse.org/api/v1/jobs/overview?distri=opensuse&version=15.3&build=9.220&groupid=77](https://openqa.opensuse.org/api/v1/jobs/overview?distri=opensuse&version=15.3&build=9.220&groupid=77). This link is assembled from the given distri, version, build and groupid. This overview returns only the job name and the job ids. So next we need to fetch the details of every single job via the corresponding `https://openqa.opensuse.org/api/v1/jobs/<$ID>` link, e.g. for [1932408](https://openqa.opensuse.org/api/v1/jobs/1932408). This is where the interesting information can be retrieved. From there we check the state of every job, and in case of a failed job, we also fetch the comments and look for a comment that tells us, that those failures can be ignored ("@ttm ignore"). We print the name of the job and color-code the line depending on the job status.

Congratulations! This is your first program that accessed the openQA API from scratch. Reading information out of the permitting openQA API can be easy.

The API also allows manipulation like comment posting, job deletion, job posting etc. Those require authentication, which we will not cover here. However, the `openqa_client` library, which we will look at next, has an implementation of the required authentication and can be used right away.


## Exercise 2: Using the `openqa_client` library

[openqa-client](https://pypi.org/project/openqa-client/) is a ready-to used python library on pypi.org that makes accessing the openQA API easy. It is still a low-level library, that requires knowledge about the openQA API paths, but still makes your life much easier when you need to do authenticated requests (POST, DELETE, ...). It can be easily installed with pip

    pip3 install openqa-client --user

And from here we start with a very basic usage example

```python
from openqa_client.client import OpenQA_Client
client = OpenQA_Client(server='openqa.opensuse.org')
print(client.openqa_request('GET', 'jobs/1'))
```

The method `openqa_request(method, path, params=None, retries=5, wait=10, data=None)` is the core of the library and where the party is going on. It requires the http `method` (GET, POST, DELETE, PUT, ...), the API path, additional request parameters and other arguments you normally don't need to worry about.

Let's write our little overview program again, using this library ([client_example.py](client_example.py)):

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from openqa_client.client import OpenQA_Client

if __name__ == "__main__":
    distri = "opensuse"
    version = "Tumbleweed"
    build = "20210921"
    job_group = 1

    ooo = OpenQA_Client(server="openqa.opensuse.org", scheme="https")

    # Note: '/api/v1' is added automatically, if the path does not start with /
    path = "jobs/overview"
    params = {}
    params['distri'] = distri
    params['version'] = version
    params['build'] = build
    params['job_group'] = job_group

    c_group = ooo.openqa_request(method="GET", path=path, params=params)
    # print(json.dumps(c_group))

    job_ids = [job["id"] for job in c_group]
    jobs = ooo.get_jobs(jobs=job_ids)
    for job in jobs:
        name = job["name"]
        state = job["state"]
        print("%-100s\t%-20s" % (name, state))
```

For some reason at the moment the build number is off by two days, this is why I'm using a hardcoded build number here (and because I'm lazy).

Other then that there are no surprises here. We don't do the parsing of the job state, which can be done completely analog to exercise 1.

Another neat feature of this library is that it loads config files from `/etc/openqa` and your home directory for you. This means that api keys and api secrets stored there are used right away. We can have nice things after all :-)

## And what about `go`?

It is no secret that I prefer statically typed programming languages like C or `go` over dynamically ones. `openqa-mon` for instance is written in `go` because I believe a whole class of errors can be evaded elegantly by this design choice. The result of almost a year playing around with `openqa-mon` is [gopenqa](https://github.com/grisu48/gopenqa), a (intentionally bad name for a) openQA client module written in `go`.

The project is in development and mostly used for `openqa-mon` and some other toy projects. It still lacks useful examples or a usage tutorial, comprehensive unit tests and serious testing in general, so it should probably not being used by anyone. However it works and if you feel brave, you can have a look at it on [GitHub](https://github.com/grisu48/gopenqa). Participation and PR are welcome!

# Summary and outlook

The openQA API is a might REST interface, that allows read and write interaction with any openQA instance. It is very useful for various monitoring and automation purposes and can be easily accessed via http requests.

This post contains two simple python programs that illustrate how the openQA API can be used. The most useful resource for exploring the capabilities is any 404 page on any openQA instance (e.g. [https://openqa.opensuse.org/api/v1](https://openqa.opensuse.org/api/v1)). This lists all possible paths and how they can be accessed.

Read-only access can be easily realised with simple http request, once the correct path is known. Browsing the "normal" openQA web UI can be useful to figure out how different parameters can be used/combined.

The openQA API also allows manipulation requests like job deletion, comment posting and the creation/schedule of new jobs. For such operations I recomment to use the already existing [openqa-client](https://pypi.org/project/openqa-client/) python library, because it abstracts the authentication from the user. It also loads the config files from `/etc/openqa` and your home directory for you.

Finally I'd like to point to `openqa-cli` (and my [cheat-sheet](/openqa/openqa-cli-cheat-sheet/) for it), which is a ready-to use CLI for interacting with the openQA API directly from the terminal. The tool `openqa-cli` has been covered already in [Cris' blog](https://kalikiana.gitlab.io/post/2021-04-27-working-with-openqa-via-the-command-line/) some time ago.
