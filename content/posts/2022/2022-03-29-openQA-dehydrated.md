---
title: openQA and dehydrated
author: phoenix
type: post
date: 2022-03-29T16:52:35+02:00
categories:
  - openQA
tags:
  - openQA
  - webui
---
In this blog post I'm gonna show you, how you can enable https for your openQA instance using `dehydrated` and the internal SUSE CA.
The same procedure should also work for Let's Encrypt.

I'm assuming you use `apache2` as the webserver for openQA.

## Setting up `dehydrated` using the SUSE CA

[dehydrated](https://dehydrated.io/) is a letsencrypt/acme implementation in bash and as such relatively simple. It requires `openssl` for handling of the keys and certificates. `dehydrated` is available as package on openSUSE Tumbleweed and Leap:

    zypper install dehydrated dehydrated-apache2

To configure `dehydrated`, you need to do three things:

1. Create a configuration file `/etc/dehydrated/config.d/suse-ca.sh`
2. Add your domain to `/etc/dehydrated/domains.txt`
3. Accept the terms by running `dehydrated --register --accept-terms`
4. Bonus: Stay dehydrated by enabling the periodic timer

### 1. Configuration

Create the `/etc/dehydrated/config.d/suse-ca.sh` file with the following contents and replace the `CONTACT_EMAIL` with your email address. It's important that the file ends in `.sh`, but it does not need to be executable.

```
CA="https://ca-internal.suse.de/acme/acme/directory"
CHALLENGETYPE="http-01"
WELLKNOWN=/var/lib/acme-challenge
HOOK="${BASEDIR}/hook.sh"
KEY_ALGO=rsa
CONTACT_EMAIL=youremail@suse.com
RENEW_DAYS="14"
PRIVATE_KEY_RENEW="yes"
```

### 2. Add your domain

Assuming you own the awesome server `duck-norris.qam.suse.de`, add this to the `/etc/dehydrated/domains.txt` file:

```
duck-norris.qam.suse.de
```

I typically clear out the file and just have a list of domains without any other template there.

Yes, this is a plain text file that contains a list of domains that dehydrated needs to manage. Nothing else.


### 3. Accept the terms

To accept the terms of usage, run:

```
root@:> dehydrated --register --accept-terms
  + Generating account key...
  + Registering account key with ACME server...
  + Fetching account URL...
  + Done!
```

This only needs to be done ones, but multiple subsequent runs don't hurt.

### 4. Stay dehydrated

Enable periodic refresh of the certificate by enabling the systemd timer:

```
systemctl enable --now dehydrated.timer
```


## Register a domain

This is the tricky part. Technically all you need to do is to run `dehydrated --cron`, and then dehydrated will run everything for you.

This does not work flawlessly with openQA, as it hijacks the passing to `.well-known/acme-challenge` via its `ProxyPass` directives. You need to disable ProxyPass for the `.well-known` location. Here you see the vhost configuration file for my own openQA instance:

```xml
<VirtualHost *:80>
    ServerName duck-norris.qam.suse.de
    ServerAdmin felix.niederwanger@suse.de

	# Prevent that openQA hijacks dehydrated
    ProxyPass /.well-known/acme-challenge !
    
    Include /etc/apache2/vhosts.d/openqa-common.inc

</VirtualHost>
```

If you need additional `Directory` directives remember, that each of them requires it's own `ProxyPass /directory !` directive, otherwise you will run into 404 errors. If you would e.g. like to add the `/srv/www/wurst` directory served as `/wurst`, it would look like the following

```xml
    ## Custom wurst directory
    <Directory "/srv/www/wurst">
        Options Indexes
        Require all granted
    </Directory>
    Alias /wurst "/srv/www/wurst"
    ProxyPass /wurst !
```

Now you can enjoy your `/wurst` 🌭

### Why don't I need to add a Directory directive?

You might ask yourself now, why don't I need to add a Directory directive for `/.well-known/acme-challenge`?
Good question, the answer is that `dehydrated-apache2` installs `/etc/apache2/conf.d/acme-challenge.conf`, which takes care of this already:

```xml
Alias /.well-known/acme-challenge /var/lib/acme-challenge
<Directory "/var/lib/acme-challenge">
   Options None
   AllowOverride None
   Require all granted
   ForceType text/plain

<IfModule !mod_access_compat.c>
   Require all granted
</IfModule>

<IfModule mod_access_compat.c>
   Order allow,deny
   Allow from all
</IfModule>

</Directory>
```

This is why you don't need to add any `Alias` or `Directory` directive anymore. You only need to prevent openQA from hijacking the `.well-known` URL for it's own purposes. Neat 🚀