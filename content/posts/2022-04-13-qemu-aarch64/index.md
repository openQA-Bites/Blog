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

The minimal example just uses your distribution pre-compiled EFI code to boot. A working example to run the disk image `openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2` is

    qemu-system-aarch64 -machine virt -cpu max -smp 2 -m 1024 -device virtio-gpu-pci \
    -bios /usr/share/qemu/aavmf-aarch64-code.bin \
    -hda openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2

To boot from an iso image and have an additional hard disk available and no graphic screen but only the serial terminal attached to the current terminal (`-nographic`):

    qemu-system-aarch64 -M virt -nographic -cpu max -smp 2 -m 1024 -device virtio-gpu-pci \
    -bios /usr/share/qemu/aavmf-aarch64-code.bin \
    -cdrom openSUSE-Leap-15.3-NET-aarch64-Current.iso -hda additional_disk.qcow2

This is the minimal working example. In the following we will go into a more extended configuration that also includes the default EFI vars.

Checkout my [run-aarch64-vm](run-aarch64-vm) script at the end for a complete example.

# Step by step guide

To run an `aarch64` image on either native aarch64 hardware or as emulated hardware, we need to do three steps:

1. Create EFI firmware and variable store images
2. Define the `machine` (suggestion: `-machine virt`)
3. Set the boot index for the image file

## Create the EFI firmware and variable store images

Ensure the `qemu-uefi-aarch64` package is installed, which provides the `/usr/share/qemu/aavmf-aarch64-code.bin` EFI boot image and `/usr/share/qemu/aavmf-aarch64-suse-vars.bin` for the default variable store.
Sidenote: Debian or Ubuntu, the firmware file is `/usr/share/qemu-efi-aarch64/QEMU_EFI.fd` from the `qemu-efi-aarch64` package.

We need to create an image file of exactly 64 MiB in size for the EFI vars and use the default provided as template:

```bash
truncate -s 64m varstore.img && dd if="/usr/share/qemu/aavmf-aarch64-suse-vars.bin" of=varstore.img conv=notrunc
```

Technically one could just use the `/usr/share/qemu/aavmf-aarch64-code.bin` file as it's read-only. I decided to ensure the size is 64 MiB because that was recommended in Will Deacon's guide:

```bash
truncate -s 64m efi.img && dd if="/usr/share/qemu/aavmf-aarch64-code.bin" of=efi.img conv=notrunc
```

Note: On Tumbleweed using `/usr/share/qemu/aavmf-aarch64-code.bin` instead of this `efi.img` runs just fine.

## Define the machine

`qemu-system-aarch64` requires the mandatory `-machine` (`-M`) argument to run. For testing purposes the generic `virt` machine might be already enough

    qemu-system-aarch64 -machine virt ...

You can list supported machines via `qemu-system-aarch64 -machine help`. The output is rather lengthy, therefore I don't put it here. `-machine virt` defaults to the latest version on your `qemu` and should be fine for most cases.

In conjunction with machine you should also configure `-cpu`. I use `-cpu max` to let qemu use the maximum available feature set. If you run into trouble, a more conservative choice would be to use `-cpu cortex-a72`, but that's up to you to decide.

## Set the boot index for the image file

Assuming we want to run the image file `openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2` you can try to just run it via

    -hda openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2

If you run into trouble with the boot order of multiple disks, then you need to add the drive as `virtio-blk` and set the bootindex to 0.

    -drive "file=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0

## Putting all things together

So, assuming we have our `efi.img` and `varstore.img` images present (See sections above), we can run the VM with out disk image `openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2` with one of the the following commands

```bash
# Minimal working configuration with no graphics window
qemu-system-aarch64 -M virt -nographic -cpu max -m 1024 -smp 2 -device virtio-gpu-pci \
-bios /usr/share/qemu/aavmf-aarch64-code.bin \
-hda openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2 

# Extended configuration
image=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2
qemu-system-aarch64 -machine virt,gic-version=max -m 1G -cpu max -smp 2 \
  -drive "file=$image,if=none,id=drive0,cache=writeback" \
  -device virtio-blk,drive=drive0,bootindex=0 \
  -drive file=efi.img,format=raw,if=pflash -drive file=varstore.img,format=raw,if=pflash
```

You can further add `-nographic` if you need to run the machine in headless mode with the serial terminal attached to the current terminal. In this case you can use `CTRL-A C` to enter the QEMU monitor and `CTRL-A X` to terminate the VM.

When running on native aarch64 hardware, you can add the `-enable-kvm` parameter to use kvm to increase the performance.

I typically re-create the efi firmware at startup to ensure I start from a clean state (see my script below). I guess one can use it across multiple machines though, so you could try to create it once and re-use it. I personally find it much easier to not care about them and just dump them after using.

# Make things easy (bash script)

"I wrote a script for that" has kinda become a running joke 😅 ... So, here it is.

I wrote a script to take the boring parts away from you. Usage:

    ./run-aarch64-vm IMAGE [OPTIONS]
    
    image=openSUSE-Leap-15.3-ARM-JeOS-efi.aarch64-2022.03.04-Build9.443.qcow2
    
    # Headless, attach serial terminal
    ./run-aarch64-vm $image -nographic
    
    # Graphic window, add HID (keyboard/mouse)
    ./run-aarch64-vm $image -device qemu-xhci -device usb-kbd -device usb-tablet

Download the [run-aarch64-vm](run-aarch64-vm) script or copy it from here:

```bash
#!/bin/bash -e

#### Settings ##################################################################
MEM="2G"
VCPU=2

## Define your disk image via program argument:
disk="$1"
# Check for empty disk and exit
if [[ -z $disk ]]; then
	echo "Usage: $0 IMAGE [OPTIONS]"
	echo "OPTIONS  - additional options passed to qemu-system-aarch64"
	echo "  e.g.   --nographic        No graphical output, attach serial terminal"
	echo "To add HID (keyboard/mouse) you need to add the following:"
	echo " -device qemu-xhci -device usb-kbd -device usb-tablet"
	exit 1
fi
shift


# Prepare EFI vars
truncate -s 64m varstore.img && dd if="/usr/share/qemu/aavmf-aarch64-suse-vars.bin" of=varstore.img conv=notrunc

# Remove efi vars file on exit
function cleanup {
	# Note: Add efi.img if you run the extended variant below
	rm -f varstore.img
}
trap cleanup EXIT

## Run VM (simple)
qemu-system-aarch64 -machine virt,gic-version=max -m $MEM -cpu max -smp $VCPU \
  -device virtio-gpu-pci -bios /usr/share/qemu/aavmf-aarch64-code.bin -hda "$disk" $@

## Run VM (extended)
#truncate -s 64m efi.img && dd if=/usr/share/qemu/aavmf-aarch64-code.bin of=efi.img conv=notrunc
#qemu-system-aarch64 -nographic -machine virt,gic-version=max -m $MEM -cpu max -smp $VCPU \
#  -drive "file=$disk,if=none,id=drive0,cache=writeback" -device virtio-blk,drive=drive0,bootindex=0 \
#  -drive file=efi.img,format=raw,if=pflash -drive file=varstore.img,format=raw,if=pflash \
#  $@
```

Have a lot of fun! 🦎