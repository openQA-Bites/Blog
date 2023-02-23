---
title: "Background bash commands"
date: 2021-02-04T14:50:02+01:00
categories:
  - openQA
tags:
  - Scripting
Summary: "This post describes the caveats and correct handling of the bash background operator within openQA."
type: post
---
Most of the openQA test cases run command sequentially. One command nicely after the next one. But in some cases it can be useful, to run a handful of commands in parallel and then wait for them to finish. Here we are covering the caveats of using the bash background operator `&` in openQA.

A TL;DR is at the end of the post.

# Usage example

For instance, in virtualization testing, we install a handful of virtual machines in parallel via ``virt-install`:

    assert_script_run('( virt-install --os-variant sles12sp3 --name sles12sp3 ... >> ~/virt-install_sles12sp3.txt 2>&1 &)');
    assert_script_run('( virt-install --os-variant sles12sp4 --name sles12sp4 ... >> ~/virt-install_sles12sp4.txt 2>&1 &)');
    assert_script_run('( virt-install --os-variant sles12sp5 --name sles12sp5 ... >> ~/virt-install_sles12sp5.txt 2>&1 &)');

The general problem is, that you would like to run a set of bash commands in parallel, and wait for all of them to complete. In terms of code, you would like to do the following:

    $ sleep 30 &         # or another command that takes some time
    $ sleep 30 &
    $ sleep 30 &
    $ sleep 30 &
    $ sleep 30 &
    $ wait

Unfortunately enclosing those comments by a simple `assert_script_run` will not work, because of the handling with the serial terminal.

    assert_script_run('sleep 30 &');       # will result in a bash syntax error

The problem is, that openqa adds something like `; echo ~59bn-\$?-"` at the end of the command, resulting in

    sleep 30 & ; echo ~59bn-\$?-

Now, `&` and `;` are both terminators in bash resulting in an empty command between those two's which is not allowed. A quick fix is to add `true` in between those twos:

    assert_script_run('sleep 30 & true');  # OK!

# Enclosing within brackets is a bad idea

Another often seen solution is to enclose the commands between brackets:

    assert_script_run('(sleep 30 & )');  # don't do that!

This is fine, unless you need to interact with your background jobs. The reason is, that the commands between the brackets are not available in the outside context. This means, bash does not keep track of those processes, so that a subsequent `wait` will not wait for those. This can be seen in the following example

    $ (sleep 30 & ); wait            # will not wait for sleep, terminates immediately
    $ (sleep 30 & ); jobs            # sleep is not visible

You can see, that the `sleep` command is not accessible in the context outside of the brackets. `wait` terminates immediately and `sleep` does not appear as a job in `jobs`. The correct way would be to omit the brackets and the semicolon:

    $ sleep 30 & wait
    [1] 12015
    
    $ sleep 30 & jobs
    [1] 12038
    [1]+  Running                 sleep 30 &

So, back to our starting point, if you enclose the commands in brackets, a subsequent `wait` will not work and this is why I believe that enclosing bash commands between brackets is a bad idea:

    assert_script_run('(sleep 30 & )');
    assert_script_run('wait');               # Will NOT wait for the sleep above!

One possible solution would be to add a `true` at the end of the `sleep` command:

    assert_script_run('sleep 30 & true');
    assert_script_run('wait');               # this would works

While thous would work, it is not really wise to use `assert_script_run` or `script_run` for background jobs. Both routines do much more than just running commands, and they might get confused by race conditions in the output or by the return value. Currently the suggested way is to use `type_string` for the background job:

    type_string("sleep 30 &\n");

And `script_run` for the `wait`. The reason to use here `script_run` is that we do not only want to type `wait`, but make openQA actually wait for that `wait` to complete

    script_run('wait');       # No "\n" here anymore, don't get confused :-)

## Why I stick to `script_run` as long as possible

You see in the code segments above, that in `type_string` you have to add a "\n" at the end of the command. Plus, that one needs to be enclosed within `""` and not `''` because Perl. Since I'm not doing background jobs so often, that this becomes a routine, this will be a source of error and frustration every time I have to re-do it.

If find this confusing and because normally it's already hard enough to figure out the other reasons why your test is failing, I'm gonna stick to `script_run`.

# TL;DR

The correct way of running bash commands in the background is

    type_string("sleep 30 &\n");     # Note: \n requires "" not ''
    type_string("sleep 30 &\n");
    script_run('wait');              # Don't use \n here!

However, I find this confusing because you need to remember that `type_string` requires `""` because of the required newline at the end. Also, don't use `type_string` for the `wait`, otherwise openQA will go on without waiting for the jobs.
This is why I'm gonna stick to `script_run` as long as possible:

    script_run('sleep 30 & true');     # works with ''
    script_run("sleep 30 & true");     # works with ""
    script_run('wait');                # no confusion with "\n" in this example

For this case, `script_run` is one unified command that behaves in the same way for all three and without those caveats.
I'm pretty sure, a lot of people will disagree with this approach though :-)