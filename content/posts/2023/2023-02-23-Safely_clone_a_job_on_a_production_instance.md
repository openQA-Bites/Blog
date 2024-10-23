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
openqa-clone-job ... _GROUP=0 [BUILD=wuseldusel] [TEST=wuseldusel]
openqa-clone-job ... _GROUP=0 {TEST,BUILD}+=-phoenix-poo123456
```

`_GROUP=0` is obligatory, `BUILD` and `TEST` are optional. If you don't set them, the cloned job will stil show up in the Next/Previous job list.

Change or remove `PUBLISH_HDD_x` variables, if present, to avoid asset overwrite.

# Cloning jobs without screwing up existing jobs

*First: [Read the documentation page on this topic](http://open.qa/docs/#_trigger_new_tests_by_modifying_settings_from_existing_test_runs) because this blog post might be outdated by the time you're reading this.*

When you use `openqa-clone-custom-git-refspec`, you're already good.

When using the `openqa-clone-job` tool you need to manually set `_GROUP=0` and a custom `BUILD` and a custom `TEST` setting.
`BUILD` and `TEST` are not strictly necessary, but if you don't set them, the new job will be still considered part of the same scenario. This means it can show up in the WebUI and in the Next/Previous jobs listing.

If preset, also change the `PUBLISH_HDD` variables to avoid that assets will be overwritten.

This is how a complete command could look like:

```
openqa-clone-job https://openqa.opensuse.org/tests/1 _GROUP=0 {TEST,BUILD}+=-phoenix-poo123456
```

Additional trick: by using `+=`, you only add the additional suffix but leave the original settings intact.

Jobs are grouped by their group id. If you set it to the non-existing group ID 0, the job won't appear in the listing, nor will it count for the original job group.

This is important, because otherwise if you clone a job, that job will become the new job on the production instance. If the job fails it might appear as a false positive to reviewers and the release automation.
Or worse, if a failed job becomes passing, you risk that someone might accidentally release a regression.

Don't do that. Use `_GROUP=0`. And modify also `BUILD` so that it will not appear in the most recent ones. Practically this is an additional safeguard.

You should also set a custom `TEST=` variable to avoid that the cloned job is being considered as part of the same scenario. This would make it show up in the job's Next/Previous tab.

And don't forget that you can (and should!) use `BUILD` for your own enjoyment. The possibilities are endless 😉

***

**Edit 2024-02-13** Updated post to use `_GROUP=0` everywhere.

**Edit 2024-10-24** Updated post to include `TEST=` everywhere.