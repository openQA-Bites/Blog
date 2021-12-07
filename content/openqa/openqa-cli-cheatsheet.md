---
title: openqa-cli cheat sheet
author: phoenix
type: page
url: /openqa/openqa-cli-cheat-sheet
date: 2021-08-19T13:46:21+02:00

---
`openqa-cli` is a command-line utility for interacting with openQA. The tool is versatile and allows you to control and interact with an arbitrary openQA instance from the comfort of your command line. While the internal help is quiet comprehensive, I list some of the most basic tasks in the form of a tutorial or knowledge base here.

Within this page the hostname `duck-norris.host` refers to a custom openQA instance. Replace it with your own hostname.

I use job id `1234` as an example ID. Replace with the actual job ID.

# How do I ...

## ... show the help message for using the API?

    openqa-cli api --help                                # Show help

## ... get a job's state?

    openqa-cli api jobs/1234
    openqa-cli api --host http://duck-norris.host jobs/1234

## ... restart a job?

    openqa-cli api -X POST --host http://duck-norris.host jobs/1234/restart

Restart a job but not its [directly chained parents](http://open.qa/docs/#_notes_regarding_directly_chained_dependencies)

    openqa-cli api --host http://duck-norris.host -X POST jobs/1234/restart skip_parents=1

## ... cancel job?

    openqa-cli api -X POST --host http://duck-norris.host jobs/1234/cancel

## ... start/post a new job?

    openqa-cli api --host http://duck-norris.host -X POST isos ARCH=x86_64 DISTRI=sle ...

This is often referred to as "isos post" because it has been used to [test an ISO image](http://open.qa/docs/#_adding_a_new_iso_to_test). Nowadays we are also testing non-iso images

### Post a new job with `json` parameters

To post a job with settings from a `json` file

    openqa-cli api --host http://duck-norris.host --data-file FILE.json --form -X POST isos

The parameters `DISTRI`, `VERSION`, `ARCH` and `FLAVOR` are then taken from the json file. The `FILE.json` looks like the following:

```json
{
    "DISTRI": "opensuse",
    "VERSION": "tumbleweed",
    "ARCH": "x86_64",
    "FLAVOR": "GCE-Updates",
    "IMAGE_ID": "image-test12345",
    "IMAGE_BASE": "publiccloud_tools.qcow2"
    "INCIDENT_ID": 12345,
    "BUILD": ":12345:kernel",
    "_OBSOLETE": "1",
}
```

## ... delete a job?

    openqa-cli api --host http://duck-norris.host -X DELETE jobs/1234
