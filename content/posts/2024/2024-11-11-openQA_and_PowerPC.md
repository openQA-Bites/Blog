---
title: openQA and PowerPC
author: phoenix
type: post
date: 2024-11-11T11:14:48+01:00
Lastmod: 2024-12-02T10:50:00+01:00
categories:
  - openqa
tags:
  - openqa
  - PowerPC
---
Due to recent changes in the worker configuration of the SUSE internal openQA instance, we needed to reconfigure some of the PowerPC jobs in openQA. This triggered a couple of questions regarding the availability of openQA worker, worker backends, their differences and their caveats. This blog post should act as a quickstart/overview guide for people getting into OpenQA testing on the PowerPC architecture.

PowerPC jobs can run in three different modi: as native virtual machines on **PowerVM**, leveraging the full power of PowerPC (pun intended!), as KVM-powered virtual machines, henceforth **KVM on PowerNV** or as [emulated PowerPC jobs](#emulated) on non-native PowerVM hardware, e,g. x86_64.
While PowerVM is the only officially recommended way from IBM, in openQA we use KVM on PowerNV successfully for years. OpenQA has backends for PowerVM and KVM on PowerNV but since both comes with different shortcoming, it is difficult to give a recommendation which one to use. Emulated PowerPC jobs should be avoided because they are very slow.

## TL;DR

* `qemu_ppc64le` is closer to openQA, while `ppc64le_hmc` is closer to PowerPC
* `qemu_ppc64le` provides a more openQA feature-complete backend
* `ppc64le_hmc` is more likely to run on more recent hardware (Power10), but comes with caveats (see [below](#caveats))
* `ppc64le_hmc` is not (yet) available on [openqa.opensuse.org](https://openqa.opensuse.org)
* Emulated PowerPC workers exist, but they are very slow. Details [see below](#emulated).

When selecting a PowerPC backend, use the [caveats section](#caveats) below for a help to decide which backend fits your use case better.

# Different virtual machine modi

On PowerPC everything is virtualized. The hardware is designed to be a hypervisor from ground up. Even in OPAL, it's most basic bare-metal configuration, the OS will run as the only VM on the internal hypervisor.

The internal hypervisor is backed directly by PowerPC and is managed by the VIOS (virtual input output server). VIOS is AIX based IO hub system which runs as a separate essential VM on the PowerPC machine itself. The customary way of managing virtual machines is to use either Novalink or HMC. HMC is an external management solution, typically running on a separate host and able to manage a cluster of PowerPC machines from one single host (similar to a Salt master). Novalink is used as internal management interface from the same host.
Those are just different ways of managing virtual machines on PowerVM.

For using PowerPC in openQA one does not need to know how the internals work, the backend should abstract this for you away.
For more information on the internals itself, I refer to the [SUSE QE Tools Workshop 2021-02-05 - PowerPC administration](https://www.youtube.com/watch?v=q1CM2AH5aKY) recording.

## OpenQA provided backends

openQA provides testing ability on PowerVM using either NovaLink or HMC. PowerPC managed over HMC is the newer backend and should be preferred over Novalink.
This is realized via the `ppc64le_hmc` backend. Although this is supported and used, those backends come with some limitations compared to the qemu backends, which in turn has also its own caveats. See the dedicated [caveats section](#caveats) below for more details.

KVM on PowerNV is "just libvirt/qemu", or "just KVM" depending on your view. For openQA, KVM on PowerNV is a worker instance spawning `qemu` virtual machines on a default SUSE/openSUSE Linux installation running on PowerPC.
KVM on PowerNV is provided via the `qemu_ppc64le` worker class and the most supported backend for PowerPC.
Be aware that our current PowerPC workers for KVM on PowerNV are all based on Power8. It is uncertain if this approach will work on newer Power platforms, e.g. Power9 or Power10.

The `qemu_ppc64le` worker class is currently the only PowerPC backend for [openqa.opensuse.org](https://openqa.opensuse.org). It runs on a Power8 machine running openSUSE Leap.

The caveats for both backends makes it difficult to give a single recommendation. In general one can say that `qemu_ppc64le` is closer to openQA, while `ppc64le_hmc` is closer to PowerPC.
The existing [caveats for ppc64le_hmc](#caveats) might also help you select a suitable backend for your needs.

## KVM on PowerNV for openQA

KVM on PowerNV is realized by running a default SUSE/openSUSE installation on PowerPC in OPAL/PowerNV mode. OPAL stands for OpenPower Abstraction Layer and is the closes you will get to a bare-metal installation on PowerPC. Only one VM instance is allowed, and it gets full access to the hardware (as far as possible). PowerNV (NV for Non-Virtualized) is the "bare-metal" platform using the OPAL firmware. This is the run mode for the workers providing `qemu_ppc64le`.

Be advised, that the current PowerPC workers for [openqa.opensuse.org](https://openqa.opensuse.org) are based on Power8 and the future for PowerNV for Power10 (and later) is uncertain.

## Emulated PowerPC in openQA {#emulated}

OpenQA allows to use qemu-emulated PowerPC virtual machines. They do work but they are very slow. To run an emulated VM, you can use the default `qemu_x86_64` WORKER_CLASS and then apply the following settings:

```
QEMU=ppc64
QEMUCPU=POWER9
QEMU_NO_KVM=1
```

Because those test runs are so slow, consider also using `TIMEOUT_SCALE=2`. This will increase all timeouts by a factor of two, so you don't need to manually increase timeouts in `script_run` and for `MAX_JOB_TIME`, and so on. This is needed, because otherwise those jobs very likely run into various timeout issues.

Emulated PowerPC jobs do work but are not recommended. Use them only if you really need to.

This configuration also works for other emulated hardware, e.g. for [emulated aarch64](/posts/2022/2022-10-04-emulated_aarch64_worker/) I wrote about some time ago.

# Known caveats {#caveats}

* `ppc64le_hmc` only supports raw images, but not `qcow` or `qcow2`
* `ppc64le_hmc` cannot publish HDDs from this backend (yet)
* `ppc64le_hmc` is not available on [openqa.opensuse.org](https://openqa.opensuse.org)
* `qemu_ppc64le` runs only on Power8 and it is uncertain if it will run on Power9 or Power10

## Further links

* [SUSE QE Tools Workshop 2021-02-05 - PowerPC administration](https://www.youtube.com/watch?v=q1CM2AH5aKY)

## Credits

Big thanks to Nick Singer, for helping to write this blog post!

***

* Edit 02.12.2024 - Added [emulated PowerPC](#emulated).