---
title: 'openQA: emulated aarch64 worker'
author: phoenix
type: post
date: 2022-10-04T08:29:20+02:00
categories:
  - openqa
tags:
  - openqa

---
Are you in dire need of an aarch64 worker on your own openQA instance, but no suitable hardware lying around?
If speed is not your main concern, then don't worry - you can just enable a qemu-emulated aarch64 worker on your openQA instance (probably x86_64). In this post we're gonna explore how to setup an emulated aarch64 qemu worker on your own openQA instance in less than 10 minutes.

### TL;DR

Install dependencies

    # zypper in qemu-arm

Configure a new worker in `/etc/openqa/workers.ini`

```ini
# /etc/openqa/workers.ini
[10]
WORKER_CLASS=qemu_aarch64
QEMU_NO_KVM=1
QEMUCPU=max
QEMUMACHINE=virt,usb=off
```

Start/enable the new worker

    # systemctl enable --now openqa-worker@10

Clone a aarch64 job (e.g. from [Tumbleweed AArch64](https://openqa.opensuse.org/group_overview/3)) to your instance to check if everything is working as expected.

## Adding an emulated worker in openQA

First, ensure you have the required packages installed. The `qemu` package you need is `qemu-arm` so that we have the `qemu-system-aarch64` command available.

    # zypper in qemu-arm

After that you need to configure a new worker with the `qemu_aarch64` worker class. OpenQA enables hardware virtualization by default via kvm, but this will not work for emulated machines. We need to turn kvm off via qemu-related variables, otherwise the machine won't boot. I also recommend to define a new worker, because the used QEMU variables have undesirable effects on your normal workers. You can pick any id (here e.g. `10`). The ids must not be subsequent, you can pick any one.

```
[10]
WORKER_CLASS=qemu_aarch64
QEMU_NO_KVM=1
QEMUCPU=max
QEMUMACHINE=virt,usb=off
```

Enable the new worker (use the same id as above)

    # systemctl start openqa-worker@10                # Start worker but don't enable it
    # systemctl enable --now openqa-worker@10         # Enable and start (i.e. start at boot)

And you're ready to rock! To test your new worker, pick any aarch64 job from [openqa.opensuse.org](https://openqa.opensuse.org) (e.g. [Tumbleweed AArch64](https://openqa.opensuse.org/group_overview/3)) and clone it to your instance.

## Caveats

* Emulated workers might be slow as molasses. This is for testing purposes only and expect timeout and other runtime-related issues
* Typical restrictions from emulated hardware apply (duh!)

***

And that's how you can easily configure an emulated aarch64 worker on your openQA instance. The same might be also working for ppc64le or s390x, but that I haven't tested (yet).
