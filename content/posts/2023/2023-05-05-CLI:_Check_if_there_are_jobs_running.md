---
title: 'CLI: Check if there are jobs running'
author: phoenix
type: post
date: 2023-05-05T09:32:47+02:00
categories:
  - openqa
tags:
  - openqa
  - cli

---
I recently automated the installation of updates on my openQA development instance. The goal was to make the instance updates itself over night, but only if it is idle, i.e. there are no running jobs. Sometimes when I'm busy, the instance needs to work overnight and despite openQA being able to restart cancelled jobs from a reboot, I prefer to avoid situations where this might result in problems in times, where I really can't have that.

So long story short: Here's how you can check, if the local (or any other) instance is currently running some jobs (i.e. jobs are being running or scheduled) or not.

```bash
#!/bin/bash -e
# Check if there are currently jobs running. Will print the number of found job and return with the same number as return value

# fail if any of the following commands fails
set -o pipefail

# fetch the current running and scheduled jobs, and count them using `jq`
rc=`curl -s --fail 'http://localhost/api/v1/jobs?state=scheduled&state=running' | jq -r '.jobs | length'`
echo $rc
exit $rc
```

I use this script to check if the instance is busy, and if so, I just skip the automatic update installer. Easy as that.

## Update and reboot, if instance is idle

And here is the cron script that I use to update the instance automatically overnight, just as a bonus.

```bash
#!/bin/bash -e
set -o pipefail


# Check for running jobs and skip, if instance is busy.
jobs=`curl -s --fail 'http://localhost/api/v1/jobs?state=scheduled&state=running' | jq -r '.jobs | length'`
if [[ $jobs -gt 0 ]]; then
    echo "Instance is busy, skipping update"
    exit 0
fi

zypper refresh
zypper -n dup
reboot
```

And thiscould be then your crontab (yes you can also use systemd timers, I was lazy here).

```
# m h  dom mon dow   command

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Update and reboot system, if system is idle
0 0 * * * /root/cron/update-system
```

Another day, another boring task automated 😀
