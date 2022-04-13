---
title: Running an aarch64 image in qemu
author: phoenix
type: post
date: 2022-04-13T09:50:46+02:00
categories:
  - virtualization
tags:
  - qemu
  - aarch64

---
Running a `x86_64` image in `qemu` machine can be as easy as:

    qemu-system-x86_64 openSUSE-Leap-15.3-JeOS.x86_64-kvm-and-xen.qcow2

	# A more extended example
    qemu-system-x86_64 -m 1G -cpu host -enable-kvm -smp cores=2,threads=1,sockets=1 -drive file=openSUSE-Leap-15.3-JeOS.x86_64-kvm-and-xen.qcow2,if=virtio

Doing the same for `aarch64` is a bit more tricky. In this tutorial we're gonna learn how to run a `aarch64` vm using `qemu`. This approach works on native aarch64 hardware and as emulated VM on any other architectures as well.

Most of this tutorial is based on Will Deacon's [Running a full arm64 system stack under QEMU](http://cdn.kernel.org/pub/linux/kernel/people/will/docs/qemu/qemu-arm64-howto.html) post, I just made it work on openSUSE and trimmed down the actual `qemu-system-aarch64` command to it's minimum.

## TL;DR

1. Create EFI firmware and variable store
2. Define the `machine`
3. Set the boot index for the image file

If you run openSUSE, you can use the following snippet to achieve all of this from the command line:

```bash
# Prepare EFI vars
qemuefi="/usr/share/qemu/aavmf-aarch64-code.bin"
truncate -s 64m varstore.img
truncate -s 64m efi.img && dd if=$qemuefi of=efi.img conv=notrunc

# Run VM with 1 GiB memory and 2 vCPUs
# Replace 'openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2' with your image
qemu-system-aarch64 -machine virt,gic-version=max -m 1G -cpu max -smp 2 \
  -drive "file=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0 \
  -drive file=efi.img,format=raw,if=pflash -drive file=varstore.img,format=raw,if=pflash
```

Checkout my [run-aarch64-vm](run-aarch64-vm) script for a complete example.

# Step by step guide

To run an `aarch64` image on either native aarch64 hardware or as emulated hardware, we need to do three steps:

1. Create EFI firmware and variable store images
2. Define the `machine` (suggestion: `-machine virt`)
3. Set the boot index for the image file

## Create the EFI firmware and variable store images

Ensure the `qemu-uefi-aarch64` package is installed, which provides the `/usr/share/qemu/aavmf-aarch64-code.bin` EFI boot image.
On Debian or Ubuntu, the file is `/usr/share/qemu-efi-aarch64/QEMU_EFI.fd` from the `qemu-efi-aarch64` package.

We need to create an image file of exactly 64 MiB in size, which contains this firmware.

```bash
qemuefi="/usr/share/qemu/aavmf-aarch64-code.bin"      # openSUSE
#qemuefi="/usr/share/qemu-efi-aarch64/QEMU_EFI.fd"    # Debian/Ubuntu
truncate -s 64m efi.img && dd if=$qemuefi of=efi.img conv=notrunc
truncate -s 64m varstore.img
```

## Define the machine

`qemu-system-aarch64` requires the mandatory `-machine` argument to run. For testing purposes the generic `virt` machine might be already enough

    qemu-system-aarch64 -machine virt ...

You can list supported machines via `qemu-system-aarch64 -machine help`. The output is rather lengthy, therefore I don't put it here. `-machine virt` defaults to the latest version on your `qemu` and should be fine for most cases.

## Set the boot index for the image file

Assuming we want to run the image file `openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2`, we need to add the drive as `virtio-blk` and set the bootindex to 0.

    -drive "file=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0

## Putting all things together

So, assuming we have our `efi.img` and `varstore.img` images present (See sections above), we can run the VM with out disk image `openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2` with the following command:

```bash
qemu-system-aarch64 -machine virt,gic-version=max -m 1G -cpu max -smp 2 \
  -drive "file=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0 \
  -drive file=efi.img,format=raw,if=pflash -drive file=varstore.img,format=raw,if=pflash
```

You can further add `-nographic` if you need to run the machine in headless mode with the serial terminal attached to the current terminal. In this case you can use `CTRL-A C` to enter the QEMU monitor and `CTRL-A X` to terminate the VM.

When running on native aarch64 hardware, you can add the `-enable-kvm` parameter to use kvm to increase the performance.

I typically re-create the efi firmware at startup to ensure I start from a clean state (see my script below). I guess one can use it across multiple machines though, so you could try to create it once and re-use it. I personally find it much easier to not care about them and just dump them after using.

# Make things easy (bash script)

"I wrote a script for that" has kinda become a running joke 😅 ... So, here it is.

I wrote a script to take the boring parts away from you. Modify it to your needs:

```bash
#!/bin/bash -e

#### Settings ##################################################################
# Memory usage (2 GiB)
MEM="2G"
# Number of virtual CPUs
VCPU=2

## Define your disk image here
#disk=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2
## or set it as program argument:
disk=$1

# Check for empty disk and exit
if [[ -z $disk  ]]; then
	echo "Usage: $0 IMAGE"
	exit 1
fi

# Prepare EFI vars
qemuefi="/usr/share/qemu/aavmf-aarch64-code.bin"
truncate -s 64m varstore.img
truncate -s 64m efi.img && dd if=$qemuefi of=efi.img conv=notrunc

# Remove efi vars file on exit
function cleanup {
	rm -f varstore.img efi.img
}
trap cleanup EXIT

# Run VM command
qemu-system-aarch64 -nographic -machine virt,gic-version=max -m $MEM -cpu max -smp $VCPU \
  -drive "file=$disk,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0 \
  -drive file=efi.img,format=raw,if=pflash -drive file=varstore.img,format=raw,if=pflash
```

Have a lot of fun! 🦎