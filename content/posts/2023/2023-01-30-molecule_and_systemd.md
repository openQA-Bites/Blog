---
title: molecule and systemd and cgroupns
author: phoenix
type: post
date: 2023-01-30T16:17:26+01:00
categories:
  - tools
tags:
  - ansible

---
It's Hackweek and I'm back at working on the [GeekOops](https://github.com/GeekOops) project. One of the more annoying tasks that I have been postponing already since some time is to adjust the molecule workflow to work with cgroups 2.

Turns out waiting helps, since recently the new `cgroupns` parameter has been introduced [[1]](https://github.com/ansible/schemas/pull/393).  
No more fiddling with the `systemd.unified_cgroup_hierarchy=0` kernel parameter that won't work in GitHub Actions, which is fantastic news!

So for my future self, this is how systemd test runs in Ansible Molecule will work now:

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: leap15_4
    image: registry.opensuse.org/opensuse/leap:15.4
    dockerfile: Dockerfile.leap15_4
    command: ${MOLECULE_DOCKER_COMMAND:-"/usr/sbin/init"}
    privileged: true
    cgroupns: host
    tmpfs:
      - /run
      - /tmp
   ...

provisioner:
  name: ansible
  inventory:
    host_vars:
      leap15_4:
        ...
      ...
verifier:
  name: testinfra
```

It's not needed to pass any `/sys/fs/cgroup` folders anymore (and you should not). the `cgroupns: host` parameter is all that's needed.

This will hopefully help to renew most of the ansible rules to more reliable molecule test runs that will help us to further improve the ansible roles.
