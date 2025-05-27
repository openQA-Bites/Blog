---
title: "How I write bugreports"
author: phoenix
type: post
date: 2025-05-27T09:06:28+02:00
categories:
  - testing
tags:
  - testing
  - softskills
draft: true
---
Writing bug reports is an important task for testers, yet there is no real unified scheme on how to write "good bug reports". In this blog post I try to summarize how I write bug reports.
This holds no authority on a definite style guide, it just serves as one example on how this can be done.

I will use https://bugzilla.opensuse.org/show_bug.cgi?id=1243645 as an example, because it combines most of the important elements of a "good bug report":

```
Created attachment 882919 [details]
WSL login with the error message

When skipping the user creation in the JeOS firstboot wizard, WSL startup throws the following error message:

> WSL (164 - Relay) ERROR: operator():420: getpwuid(1000) failed 2

This is understandable, as WSL tries to login as user with UID 1000, which doesn't exist. So, the problem is that the JeOS firstboot wizard allows to skip the user creation, but then starting WSL results in a state that throws the above stated error message.

I still am able to get a WSL shell as root, which seems to work fine.

I wonder, if we should allow to skip the user creation, or create a default user without asking - given that WSL apparently assumes that a user with UID is present. The bug is IMHO to allow skipping the user account, when it is implicitly required.

## Reproducer

In Powershell:

> wsl --install --distribution openSUSE-Tumbleweed
> wsl.exe -d openSUSE-Tumbleweed

Then follow through the installation wizard, and skip the user creation.
```

But before we start a short disclaimer.

### Disclamer

**None of the rules here are written in stone.**

A two-sentence summary can be a three-sentence summary. Or a one-sentence summary. The Impact can be last. Or first. Additional information can be before the rproducer. More sections can be present. Sometimes just a summary is enough. It all depends on the required depth of information and what you want to tell.

This is a guideline, not a law. It's not even a codex. It's my personal opinion.

## The structure

I try to typically follow the following structure for a bug report:

1. Two-sentence summary (obligatory)
2. Context and description (obligatory)
3. Impact (if possible)
4. Everything else (if required)
5. Reproducer (obligatory if possible)
6. Workaround (if applicable)

Let's go through each of those items one by one.

### Two-sentence summary

This part is obligatory and is probably the most imporant and most difficult part of the bug report. This is written last.

One more time again, because this is important: This part gets written last, after everything else has been written. **Those two sentences are the most important part of the whole bugreport.**

To understand why this is so important: Put yourself into the shoes of anyone who reads the bug report.
This is the executive summary. The elevator pitch. The mission critical overview report. The radio message from the scene. You're the first responder and need to tell the other side what the situation is in two sentences because someone's life depends on it (hopefully it doesn't, but you get the gist).
This message allows the reader to decide if this is relevant for them and if the rest of the bug is worth (or necessary) to read or not. This is the lobby, the receptionist and the welcome part of your bug report.

**Every reader should have an idea what the overall problem is after reading only those two sentences.**

A good bug report distills the relevant information and cuts down the noise. You cannot expect that everyone will read through an essay, consisting of 100 lines of text output (where only 2 lines in the middle matter). It is your job to distill the essence and summarize it. Your audience will appreciate it.

But what is the target audience? Turns out it is surprisingly large. Bug reports get read by developers, testers, release managers, users, and others. And you need to consider all of them.
A bug report might be read first by someone doing a priority triage. It then gets assigned to a developer for a fix.
After fixing, it might be consumed by other testers, who evaluate if the filed bug has been fixed and if the fix is effective (they need reproducers! but that's for later).
Release managers need to read bug reports to understand the state of their product and if they can release or not.
And lastly, users might find them if they are affected and search for a solution or a workaround.
And all of them should just read the first two sentences to get an overall picture. Assume every one of them is in a haste and don't want to read the full bugreport just to get an overview. And all of them appreciate it, if you are capable of summarizing the whole thing in two sentences at the beginning of the bug report.

To summarize: I try to summarize the overall bug, it's impact and the very simplified context in two sentences at the beginning of every bug, so that everyone has an overall picture after reading them. One should be able to decide if it's worth reading the full description or not afterwards. One should know what's rougly going on here.

When writing a more complex bug report, this is the last part that I write. Because only after I've written the rest, I know enough that I can summarize the full picture into what really matters. This is why this part gets written last, at least for non-trivial bug reports.

***

Ok let's see this in action:

```
When skipping the user creation in the JeOS firstboot wizard, WSL startup throws the following error message:

> WSL (164 - Relay) ERROR: operator():420: getpwuid(1000) failed 2
```

Do you have a rough idea what's going on? (I hope the answer is yes). Let me break the most important parts down for you here:

* WHAT: What is the issue ? - "WSL startup throws the following error message: ..."
* CONTEXT: When does this happen? - "When skipping the user creation in the JeOS firstboot wizard" and also "WSL startup"
* SCOPE: Which product/package? - "WSL startup" and Tumbleweed in the product settings of the bug header (not shown here)

I aim to answer three questions in the summary: WHAT happens? What is the CONTEXT? And what is the SCOPE (i.e. which package/product)?

### Context and description

After the summary comes the description in more details. This section typically exists outside the scope of the summary, so it is totally fine to duplicate the information from the summary. This section should describe the bug and the context in detail.

Not every bug needs this section. The above provided example is so simple, that the description just adds to the summary. If in doubt, treat the description as a standalone part that should be self-contained. But be aware that this is no strict requirement, especially not for trivial bug reports.

After reading the context and description section, a developer should understand what the problem is and what the circumstences are, under which the issue arises. I state that a developer should understand it, because this is typically not for the general reader but the in-depth details and descriptions that is required by the developer, but not by other readers like testers, release managers and users. It is ok if those target groups don't fully understand this part, as it can get technical and complex, while the summary must not.

Information that might be fitting in here:

* Since when is this failing? (Works with build 1.2.3, fails with 1.2.4)
* What packages are affected and what versions?
* Really everything technical in the required detail

***

In the example above, I only extend the summary, because the problem was so simple that I didn't seem it fitting to re-write the summary again. For more complex issues it's better if you just assume the summary doesn't exist.

```
When skipping the user creation in the JeOS firstboot wizard, WSL startup throws the following error message:

> WSL (164 - Relay) ERROR: operator():420: getpwuid(1000) failed 2

This is understandable, as WSL tries to login as user with UID 1000, which doesn't exist. So, the problem is that the JeOS firstboot wizard allows to skip the user creation, but then starting WSL results in a state that throws the above stated error message.
```

Here it gives more context about what happend: "WSL tries to login as user with UID 1000, which doesn't exist". This is not always possible, as it often requires in-depth knowledge about the package itself, which you might not have. That's ok, just describe the problem that you see.

This part also should describe the context and conditions under which the problem arises. That's not required for this bug, as it always happens when skipping the user creation, but for others this might be necessary. If you have a problem that only occurs after three reboots, this information goes here. If the problem only happens when the user configures the package in a certain way, this information goes in here. This paragraph describes the context and the environment, in which the problem occurs in detail. After this paragraph it should be clear, when the problem arises and what the actual problem is from your point of view.

Be explicit in what you see as the problem. This section is a little bit subjective and it should also be. This is your point of view on a certain problem. Don't assume that the other side will come to the same conclusions as you do, when presenting the "facts". You should describe, why you see those facts as a problem. 

Take the example above:

> So, the problem is that the JeOS firstboot wizard allows to skip the user creation, but then starting WSL results in a state that throws the above stated error message.

Here I write where **I** see the problem. It's written in an objective way, but it expresses my subjective view on the situation. I see it as a problem, that on WSL it is possible to skip the user creation and then the system is in a state, where it will throw an error. This part is important - be explicit in where you see the problem, and present all facts to proof your point. People can argue about this POV later on, your job is to express yourself in a way that is concise and understandable.

It's ok if people disagree with your assessment later on. Your job is to first express why you see this as a problem. First make it clear why this is a problem. If you can describe the problem well, you're job is done. The goal is information clarity, not to form consensus. That's for the upcoming discussion later on in the bug.

### Impact

Write the impact of the bug on the system, if possible. This typically requires domain knowledge, so depending on your skill level and the component you file a bug against, this might be something you cannot have a judgement on. That's fine. Then just skip it.

This part is optional. Write it if you can, but otherwise just leave it out.

***

```
I still am able to get a WSL shell as root, which seems to work fine.
```

In the example above I state, that WSL remains functional and I do not see any immediate problems with it.

### Everything else

```
I wonder, if we should allow to skip the user creation, or create a default user without asking - given that WSL apparently assumes that a user with UID is present. The bug is IMHO to allow skipping the user account, when it is implicitly required.
```

Here goes everything else. I felt that the problem of the bug is ambiguous, so I thought it might be good to outline again where I see the actual problem.

Other information that could be here: Previous builds (e.g. this fails since Tumbleweed 2038-01-01, worked fine on 20237-12-31), Screenshots, Logs, ...


### Reproducer

Providing a viable, minimal reproducer sometimes makes the difference between a bug report, which will get ignored and one that gets fixed. The reproducer allows developers to reproduce and understand the bug, and start to investigate where the actual problem lies.

A reproducer also allows other testers to validate if a bugfix was effective.

Never assume that a reproducer is clear from the description. Different people have different knowledge and skills, and something that is immeditale clear to you might be something that another tester has no idea about. This is why a clear reproducer is so valuable. It gives testers and developers a recipe to reproduce and validate the bug, even if they do not know the package in depth.

For a reproducer, minimalism is king. Here, perfection is, when you cannot leave anything out. In a provided reproducer, every step should be required. Cut the irrelevant parts. Just leave the curcial parts that are required, nothing more.

Writing this part is also difficult and typically requires some fiddling, trying out and testing.
I'm typically very happy when I find a reproducer and then proceed to see if all steps are required. This means going through your reproducer multiple times, removing parts, checking, removing some more, checking again and so on ... Might sound wasteful but it's effort well spent, because your fellow developers and testers will not have to do unnecessary steps afterwards. And neither will you, in case there are follow-up questions and you need to investigate. Sure this takes time, but this is worth the effort, as everyone benefits from it. Make it small, but don't leave out any important parts. Distill it. Just leave the essence.

Often it's simply not possible to find a reproducer. That's fine. Provide one when you can. If you cannot, it sometimes is also useful to state why you can't - perhaps a developer (or someone else) can help out.

And never ever point to openQA as reproducer. Nobody else than openQA gurus can use that. Think of your audience - Will they be able to follow the steps? Likely not. A link to openQA is additional information, but this doesn't replace a well-written reporducer. Think of your target audience, probably you are the only one with sufficient openQA knowledge where such a link might be useful. It won't for anyone else.

***

### Reproducer

```
In Powershell:

> wsl --install --distribution openSUSE-Tumbleweed
> wsl.exe -d openSUSE-Tumbleweed

Then follow through the installation wizard, and skip the user creation.
```

I couldn't make it simpler. Goal reached.

### Workaround

Some of the readers of your bug wil be affected users, who search for a solution for this problem. If you found or know a workaround, feel free to share it with them. They will be thankful.

(Spoken from someone who was thankful countless times when someone posted a workaround)


## The title

Did you see that at no point until now I mentioned the title? It's because I see the bug report itself and the title as two completely different things.

The title should be explanatory so that people remember what this is about, whenever they see this bug in a list of bugs. In my view, it must not be complete, just descriptive enough to remember what this is about after reading the two-sentence summary.

The title is mostly there so that people have a clue what the bug is about when seeing it in a list or getting a notification. The title must not be a exhaustive description, just enough to get a quick grasp.
