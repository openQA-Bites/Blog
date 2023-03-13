---
title: 'openQA: Could not configure /dev/net/tun (tap3): Operation not permitted'
author: phoenix
type: post
date: 2023-03-13T14:58:18+01:00
categories:
  - openqa
tags:
  - openqa

---
I recently encountered a new interesting openQA issue:

```
[2023-03-13T14:18:22.651705+01:00] [warn] [pid:18929] !!! : qemu-system-x86_64: -netdev tap,id=qanet0,ifname=tap3,script=no,downscript=no: could not configure /dev/net/tun (tap3): Operation not permitted
```

This is an error that you likely are encountering on a older openQA instance, after you setup multimachine jobs but haven't used them in a while. For me the solution was to grant the `CAP_NET_ADMIN` capabilities to the qemu binary (again):

    setcap CAP_NET_ADMIN=ep /usr/bin/qemu-system-x86_64

Doing this step is documented in the [open.qa docs](https://open.qa/docs/#_grant_cap_net_admin_capabilities_to_qemu) and I am certain that I did this already. My hypothesis is that a recent update removed the capabilities and therefore denying the permission to the openQA worker. Resetting the capabilities resolves the issue.

# Weblinks

* https://open.qa/docs/#_tap_based_network

