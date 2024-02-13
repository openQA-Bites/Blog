---
title: Safely clone a job on a production instance
author: phoenix
type: post
date: 2023-02-23T14:42:22+02:00
Lastmod: 2024-02-13T10:34:18+02:00
categories:
  - openqa
tags:
  - openqa
---
When developing new openQA tests you will have to run a lot of verification and debug test runs.
This is why I typically encourage people to do all openQA testing on their own instances, to prevent spamming of the production instances.

However there are situations, in which you can't do everything on your own instance. Examples of such situations are runs on different architectures, or if you rely on the network infrastructure of the production instance.

### TL;DR

Use `openqa-clone-custom-git-refspec`, which already takes care of those things for you. Or:

```
openqa-clone-job ... _GROUP=0 [BUILD=wuseldusel]
```

`_GROUP=0` is obligatory, `BUILD` is optional.

Change `PUBLISH_HDD_x` variables, if present, to avoid asset overwrite.

# Cloning jobs without screwing up existing jobs

When you use `openqa-clone-custom-git-refspec`, you're already good. Otherwise just set `_GROUP=0`. Done. You're good. Bonus points for also modifying `BUILD`, but that's not strictly necessary. `BUILD=` (empty or not set `BUILD` variable) is used by [geekotest](https://github.com/os-autoinst/openqa_review) is possible but can screw up the WebUI if used wrongly. Use any other string that marks it as your playground runs, e.g. `BUILD=20230223-phoenix-test`. Adding a date is useful.

If preset, also change the `PUBLISH_HDD` variables to avoid that assets will be overwritten.

Jobs are grouped by their group id. If you set it to the non-existing group ID 0, the job won't appear in the listing, nor will it count for the original job group.

This is important, because otherwise if you clone a job, that job will become the new job on the production instance. If the job fails it might appear as a false positive to reviewers and the release automation.
Or worse, if a failed job becomes passing, you risk that someone might accidentally release a regression.

Don't do that. Use `_GROUP=0`. And modify also `BUILD` so that it will not appear in the most recent ones. Practically this is an additional safeguard.

And don't forget that you can (and should!) use `BUILD` for your own enjoyment. The possibilities are endless 😉

***

**Edit 2024-02-13** Updated post to use `_GROUP=0` everywhere.