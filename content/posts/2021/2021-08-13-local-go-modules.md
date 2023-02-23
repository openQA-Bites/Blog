---
title: Use local go modules
author: phoenix
type: post
date: 2021-08-13T10:58:14+02:00
categories:
  - src
tags:
  - go

---
When dealing with go modules, sometimes it's handy to test some changes from a local repository instead of using the upstream one.

Now, go programs are typically relying only on the upstream packages. Take the module file of `openqa-mon` as example:

    module github.com/grisu48/openqa-mon
    
    go 1.11
    
    require (
    	github.com/BurntSushi/toml v0.3.1
    	github.com/grisu48/gopenqa v0.3.3
    	github.com/streadway/amqp v1.0.0
    )

When working on `openqa-mon`, I have to often also work on [gopenqa](https://github.com/grisu48/gopenqa), my underlying go library for accessing openQA - with an intentional horrible name ;-)
Now, before pushing some testing changes online, I'd like to see if they are compatible with my current state in openqa-mon. This is where the `replace` keyword comes in handy.

Instead of relying on the upstream version, you can redirect go to look in a local directory for a certain module. See the syntax of the replace keyword

    replace github.com/somedude/someproject => /path/to/local/repository

And here is a concrete example of how I use it

    module github.com/grisu48/openqa-mon
    
    go 1.11
    
    require (
        github.com/BurntSushi/toml v0.3.1
        github.com/grisu48/gopenqa v0.4.1
        github.com/streadway/amqp v1.0.0
    )
    
    replace github.com/grisu48/gopenqa => /home/phoenix/Software/gopenqa

Now instead of using the upstream version, the local repository get used and you can test/use your local changes. Cheers.

## References

* [golang.org/ref/mod#go-mod-file-replace](https://golang.org/ref/mod#go-mod-file-replace)
