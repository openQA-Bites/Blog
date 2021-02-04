---
title: "Background Scripts"
date: 2021-02-04T14:50:02+01:00
categories:
  - openQA
tags:
  - Scripting
---
Most of the openQA test cases run command sequentially. One command nicely after the next one. But in some cases it can be useful, to run a handful of commands in parallel and then wait for them to finish. Here we are covering the caveats of using the bash background operator `&` in openQA.

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

The correct solution would be to add a `true` at the end of the `sleep` command

    assert_script_run('sleep 30 & true');
    assert_script_run('wait');               # this works