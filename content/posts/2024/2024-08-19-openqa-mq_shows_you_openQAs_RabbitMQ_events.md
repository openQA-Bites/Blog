---
title: "openqa-mq shows you openQA's RabbitMQ events"
author: phoenix
type: post
date: 2024-08-19T07:55:19+02:00
categories:
  - openqa
  - tools
tags:
  - openqa
  - tools
  - cli
---
`openqa-mq` is a small CLI tool that receives openQA related events from RabbitMQ. It is part of the `openqa-mon` packages and will work for OSD and for OOO.

RabbitMQ is a messaging broker, similar to MQTT but a bit more difficult to handle. `openqa-mq` is for you, if you just want to listen to it and wait for a certain event.

There are two pre-defined options: `--osd` and `--ooo` (or `--o3`) in order to configure `openqa-mq` to listen on OSD and on openqa.opensuse.org respectively. All you need to do is to run the application with either one of them and `openqa-mq` will print all openqa-related events of that instance:

```
$ openqa-mq --o3
RabbitMQ connected: rabbit.opensuse.org
opensuse.openqa.job.done {"ARCH":"x86_64","BUILD":"20240818","FLAVOR":"NET","ISO":"openSUSE-Tumbleweed-NET-x86_64-Snapshot20240818-Media.iso","MACHINE":"64bit","TEST":"lxde","bugref":null,"group_id":1,"id":4413831,"newbuild":null,"reason":null,"remaining":233,"result":"passed"}
opensuse.openqa.job.done {"ARCH":"aarch64","BUILD":"20240818","FLAVOR":"DVD","HDD_1":"opensuse-Tumbleweed-aarch64-20240818-gnome-x11@aarch64.qcow2","ISO":"openSUSE-Tumbleweed-DVD-aarch64-Snapshot20240818-Media.iso","MACHINE":"aarch64","TEST":"gnome-x11-ibus","bugref":null,"group_id":3,"id":4414334,"newbuild":null,"reason":null,"remaining":232,"result":"passed"}
opensuse.openqa.job.create {"ARCH":"aarch64","ASSET_256":"openSUSE-Tumbleweed-NET-aarch64-Snapshot20240818-Media.iso.sha256","BACKEND":"qemu","BOOTFROM":"cdrom","BOOT_HDD_IMAGE":"1","BUILD":"", ... }
```

For additional command line arguments use the integrated `--help` command.

`openqa-mq` is part of the `openqa-mon` package available on Tumbleweed and on Leap.
