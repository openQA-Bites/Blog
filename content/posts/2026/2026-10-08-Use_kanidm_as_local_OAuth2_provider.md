---
title: 'Use kanidm as local OAuth2 provider for openQA'
author: phoenix
type: post
date: 2026-10-08T10:56:58+02:00
categories:
  - openqa
tags:
  - openqa
---
Current openQA implementations do not offer a local user management method. This is why I use [kanidm](https://kanidm.com/) as a local identity management platform which is used for user management on my own openQA development instance. This is certainly overkill for most users and I only use it because I like `kanidm` and because all bits and bolts run locally on a single openQA instance.

## Kanidm pre-requirements

I assume you have a running `kanidm` instance somewhere. This can be on the openQA instance itself, but also elswehre. This instance needs to be reachable via `https`, including proper certificate handling. Self-signed certificates are typically not supported and will likely not work. In my setup I decided to re-use the existing ACME certificated from `dehydrated` on a custom port. So `kanidm` will be running on `https://duck-norris.qe.suse.de:8443` for throughout this tutorial.

# Kanidm configuration

`kanidm` does an excellent job in documenting the bits and bolts needed for [OAuth2](https://kanidm.github.io/kanidm/stable/integrations/oauth2.html) itself. So we'll mostly use the provided [Configuration section](https://kanidm.github.io/kanidm/stable/integrations/oauth2.html#configuration) from there and modify this to our needs.

First you'll need to login as `admin_idm`. Then you can configure a OAuth2 service for `openQA` here (or choose your own name):

```sh
kanidm system oauth2 create openQA "openQA on duck-norris" "https://duck-norris.qe.suse.de/"
kanidm system oauth2 add-redirect-url openQA "https://duck-norris.qe.suse.de/login"
kanidm system oauth2 get openQA                                        # check configuration
kanidm system oauth2 prefer-short-username openqa
kanidm system oauth2 warning-insecure-client-disable-pkce openqa       # required by openQA
```

Next we need to add a group and users who are allowed to login to this service. I use the `openqa_users` group and add my own user `phoenix` to it:

```sh
kanidm group create openqa_users
kanidm system oauth2 update-scope-map openqa openqa_users openid email profile
kanidm group add-members openqa_users phoenix
```

With this in place, we also need the `SECRET` value for the openQA configuration. This was hidden in the `kanidm system oauth2 get openQA` for security reasons and can be shown with

```sh
kanidm system oauth2 show-basic-secret openQA
```

Write the key down, we'll need it in the next section.

# openQA configuration

See the following template for your `/etc/openqa/openqa.ini`:

```ini
[auth]
method = OAuth2

[oauth2]
provider = custom
unique_name = kanidm
key = KEY
secret = SECRET
authorize_url = https://KANIDM_HOST/ui/oauth2?response_type=code
token_url = https://KANIDM_HOST/oauth2/token
user_url = https://KANIDM_HOST/oauth2/openid/KEY/userinfo
token_scope = openid email profile
token_label = Bearer
id_from = sub
nickname_from = preferred_username
```

Here `KANIDM_HOST` is your host (if needed with a port), `KEY` is the service name from above (`openQA`) and `SECRET` is the noted secret from the last section. In my case the config looks like the following

```ini
[auth]
method = OAuth2

[oauth2]
provider = custom
unique_name = kanidm
key = openqa
secret = not_telling_you
authorize_url = https://duck-norris.qe.suse.de:8443/ui/oauth2?response_type=code
token_url = https://duck-norris.qe.suse.de:8443/oauth2/token
user_url = https://duck-norris.qe.suse.de:8443/oauth2/openid/openqa/userinfo
token_scope = openid email profile
token_label = Bearer
id_from = sub
nickname_from = preferred_username
```

And with this configuration I could use `kanidm` as local identity provider for openQA.
