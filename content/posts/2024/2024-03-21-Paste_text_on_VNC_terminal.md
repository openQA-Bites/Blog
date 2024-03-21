---
title: Paste text on VNC terminal
author: phoenix
type: post
date: 2024-03-21T10:06:56+01:00
categories:
  - openqa
tags:
  - openqa
  - tools
  - vnc
---
A coworker recently faced the problem to copy&pasting a large amount of text into a VNC terminal for openQA. VNC doesn't always allow copy&paste and when you have to manually type a longer string this is prone to typos and human error.

I'd like to just share [Michael's snippet](https://gist.github.com/michaelgrifalconi/ff9789f41d922d404de45d4c95af4211) that will "type" the clipboard contents to VNC for you:

* Pre-type (or paste) script on terminal
* Copy data into clipboard
* Run the script
* Move focus to destination target (you have 5 seconds to do so)
* Script will "type" for you

```
sh -c 'sleep 5.0; xdotool type --delay 100 "$(xclip -o -selection clipboard)"'
```

I hope this makes your day a little bit better.
