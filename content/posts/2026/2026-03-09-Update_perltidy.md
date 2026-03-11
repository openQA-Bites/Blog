---
title: 'Updating perltidy (and other dependencies) in os-autoinst'
author: phoenix
type: post
date: 2026-03-09T10:17:05+01:00
categories:
  - openqa
  - tools
tags:
  - openqa
  - tools
---
When updating the `dependencies.yaml` file in [os-autoinst](https://github.com/os-autoinst/os-autoinst), e.g. when you'd like to [fix the outdated perltidy version in the repo](/posts/2022/2022-03-04-perltidy/) the recommended workflow is to:

* Update `dependencies.yaml`
* Run `make update-deps`

This will update the `cpanfile` for you and you only need to make your changes in one single file (`dependencies.yaml`).

See also https://github.com/os-autoinst/os-autoinst/pull/2822 for a template on how to create a MR for updating an outdated perltidy definition.
