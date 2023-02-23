---
title: Hide IDE folders in git using a global gitignore
author: phoenix
type: post
date: 2021-04-23T10:52:47+02:00
categories:
  - git
tags:
  - git
  - Codium

---
Integrated development environemnts (IDE) are using their own folders withing your code repositories to store their settings.
This can become annoying when working on a git repository and they keep popping up as untracked files:

```bash
$ git status
On branch master
Your branch is up to date with 'origin/master'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.vscode/

no changes added to commit (use "git add" and/or "git commit -a")
```

In my case the culprit is [VS Codium](https://vscodium.com/), a community-driven freely licensed version of VS Code.

# The problem

For some time I've been adding things like the following to my own git repos:

    .vscode
	.idea
	# ... and whatever new folders are popping up

This is a dirty approach that perhaps is fine for my own private repos as I don't switch IDEs too often.

But it certainly does not scale for large public repos with multiple people working together.
If everyone would push the folders for their own IDE, it becomes certainly a mess.

# Solution: use a global gitignore

My solution is now to use a custom global `.gitignore` in my home folder, which hides those directories for me without interfering with the actual repos.

First, create the `.gitignore` file in your home directory and put whatever files/folder you'd like to ignore in there

    vim ~/.gitignore

Mine for instance looks very simple:

    # Ignore IDE specific folders
	.vscode

Next, configure git to include this global `.gitignore` by running

    git config --global core.excludesfile ~/.gitignore
