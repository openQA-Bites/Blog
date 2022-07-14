---
title: 'openqa: asset download request but no domains passlisted'
author: phoenix
type: post
date: 2022-07-14T13:23:55+02:00
url: /posts/2022-07-14-asset_download_request_but_no_domains_passlisted/
categories:
  - openqa
tags:
  - openqa
  - troubleshooting
  - cli

---
**Symptom**

When posting a job using , you see an error message of the following kind:

```
$ openqa-cli api -X POST isos ...
403 Forbidden
Asset download requested but no domains passlisted! Set download_domains.
```

**Solution**

* Avoid passing settings with a `_URL` suffix.
* Allow the source domain by configuring `download_domains` in `/etc/openqa/openqa.ini`

**Reason**

You probably have somewhere in your POST a setting with the `_URL` suffix. Settings with `_URL` are reserved by openQA for automatic asset fetching. e.g. you can download an asset from a URL and use this as your main hard disk:

    HDD_1=remote_asset.qcow2
    HDD_1_URL=http://my-magic.pot/remote_asset.qcow2

Here, openQA would download the asset from the given URL and use it then as the primary hard disk defined in `HDD_1`.

There is however a limitation on the allowed domains configured in your `openqa.ini`. Check your `/etc/openqa/openqa.ini` file for the following section:

```ini
## space separated list of domains from which asset download with
## _URL params is allowed. Matched at the end of the hostname in
## the URL. with these values downloads from opensuse.org,
## dl.fedoraproject.org, and a.b.c.opensuse.org are allowed; downloads
## from moo.net, dl.opensuse and fedoraproject.org.evil are not
## default is undefined, meaning asset download is *disabled*, you
## must set this option to enable it
download_domains = fedoraproject.org opensuse.org
```

Here `download_domains` acts as safeguard to allow only download from allowed domains. Add your domain here, and you should be good to go.

### Job settings are not affected

At least on my openQA instance, the issue only arises if you pass the `_URL` variable via the CLI. If those variables are being set by the job groups, then the issue does not arise.
