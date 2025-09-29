---
title: Upgrade a PostgreSQL container to a new major version
author: phoenix
type: post
date: 2023-11-23T16:09:52+01:00
categories:
  - containers
  - server
tags:
  - containers
  - sysadmin
---
[PostgreSQL](https://www.postgresql.org/) is a capable and mature database, which comes in a major or minor version number (e.g. `16.0`). Minor releases never change the internal storage, so the database always remains compatible with earlier and later minor releases. However major version releases do not have such a guarentee. We are running a single PostgreSQL database as a `podman` container and I recently (today) had the glorious task of migrating this database to the next major version. In this blog post I describe how we did this migration.

***

## TLDR

* Create a new container with the target version of PostgreSQL
* Dump all data from the old PostgreSQL version to a file via `pg_dumpall`
* Import the data into the new container
* Copy the configuration file (`pg_hba.conf` and `postgresql.conf`)
* Remove the old container and use the new volume/data directory of the new container

I think this is the easiest way for small to mid size databases. There is a `pg_upgrade` tool, but I failed to get it working within a container, due to the missing binaries of the old/new PostgreSQL version. If you have a good way of doing this, please email me!

***

# Migrate a PostgreSQL container to a new major version

For this tutorial we create a new PostgreSQL container of version 15. We are going to migrate the data of this container to a new PostgreSQL container version 16. The process is based on `podman` volumes, but works also with bind mounts (see below).

## Create a new PostgreSQL container (Version 15)

Let's create a new container with a volume and PostgresSQL version 15. I will use the password `passw0rd` in this tutorial and assume you know that this password is only here for demo purposes. Please use a safe password.

```
# podman volume create postgresql
postgresql
# podman run --rm -itd -e POSTGRES_PASSWORD=passw0rd -v postgresql:/var/lib/postgresql/data:Z --name postgresql docker.io/library/postgres:15
9397d8d0ff3d93bf9d24f136d1ce38b58b8423867849332f884bf60563f8f3b2
```

Now you should have a PostgreSQL 15 container running. The `:15` tag keeps you always on the most recent minor version. You can connect to this server, if you publish the 5432 port (add `-p 5432:5432`) and run e.g. `psql` via

```
# podman exec -ti -u postgres postgresql15 psql
psql (15.5 (Debian 15.5-1.pgdg120+1))
Type "help" for help.

postgres=#
```

This container is ephemeral. When it stops it will be deleted (That's the `--rm`). This is ok, because the data is in the `postgresql` volume and you can just create a new container.

## Create the destination volume and container

For the migration, we will migrate the existing data over into a new container (and new volume). We need to create them in the same way as we have created the original container but will use version 16.

> Note: On newer versions the path is `/var/lib/postgresql`

```
# podman volume create postgresql16
postgresql16
# podman run --rm -itd -e POSTGRES_PASSWORD=passw0rd -v postgresql16:/var/lib/postgresql/data:Z --name postgresql16 docker.io/library/postgres:16
4098c5cda558b12c9001a3e56223d2a47b9dcfb08e21a5d6afa1d30052e5b28e
```

At this point you should have two PostgreSQL containers running

```
# podman ps
CONTAINER ID  IMAGE                          COMMAND     CREATED         STATUS         PORTS       NAMES
9397d8d0ff3d  docker.io/library/postgres:15  postgres    2 minutes ago   Up 2 minutes               postgresql
4098c5cda558  docker.io/library/postgres:16  postgres    24 seconds ago  Up 24 seconds              postgresql16
```

We will now migrate the data from one to the other.

## Migrate the data from one container to the other

We are using the `pg_dumpall` tool to export the data and then import it via `psql` into the destination container. We will be using a temporary `dump` file, but in principle you can also directly pipe the two.

    # podman exec -t -u postgres postgresql pg_dumpall > dump
    # less dump               # check file
    # podman exec -i -u postgres postgresql16 psql < dump
    ...

Important: Check the `dump` file before importing it! It can be that there are warning messages, which you need to remove. Those warnings will typically disappear after a fresh import. Such a warning could look like the following:

    WARNING:  database "postgres" has a collation version mismatch
    DETAIL:  The database was created using collation version 2.31, but the operating system provides version 2.36.
    HINT:  Rebuild all objects in this database that use the default collation and run ALTER DATABASE postgres REFRESH COLLATION VERSION, or build PostgreSQL with the right library version.

We also want to migrate the most important configuration files: `pg_hba.conf` and `postgresql.conf`. This can be done via the `podman cp` command.

    # podman cp postgresql:/var/lib/postgresql/data/pg_hba.conf postgresql16:/var/lib/postgresql/data/pg_hba.conf
    # podman cp postgresql:/var/lib/postgresql/data/postgresql.conf postgresql16:/var/lib/postgresql/data/postgresql.conf

You will need to restart the PostgreSQL 16 container to have those new configuration files also loaded.

After the migration is done, you can remove the old container and continue with the new container. Check if everything is ok, and then consider deleting the old volume as well.

    # podman stop postgresql

## Renaming the volume

In this example we are using the `postgresql` for the main PostgreSQL server and we used `postgresql16` for the new version. You might want to rename `postgresql16` to `postgresql` after completion. We can do this via export/import.

    # podman rm postgresql
    # podman volume export postgresql16 | podman volume import postgresql -
    # podman volume rm postgresql16

***

# Migrating PostgreSQL with bind volumes if PostgreSQL is running as systemd unit

The above was a constructed example that should allow you to follow it through for your concrete setup. There might be some differences though. In here I will guide you through our concrete scenario, which is based on bind volumes our PostgreSQL runs as a systemd unit. This makes the procedure a bit different, but the overall process is the same as above.

Let's say the PostgreSQL systemd unit looks as follows (auto generated via `podman generate systemd`).

```ini
# /etc/systemd/system/postgresql-container.service
[Unit]
Description=PostgreSQL 15 container
Wants=network-online.target
After=network-online.target
RequiresMountsFor=%t/containers

[Service]
Environment=PODMAN_SYSTEMD_UNIT=%n
Restart=on-failure
TimeoutStopSec=70
ExecStartPre=/bin/rm -f %t/%n.ctr-id
ExecStart=/usr/bin/podman run \
    --cidfile=%t/%n.ctr-id \
	--cgroups=no-conmon \
	--rm \
	--sdnotify=conmon \
	--replace \
	-itd \
	-e POSTGRES_PASSWORD=passw0rd \
	-p 5432:5432 \
	-v /srv/postgresql:/var/lib/postgresql/data:Z \
	--name postgresql \
	--memory 512M \
	--label io.containers.autoupdate=image \
    docker.io/library/postgres:15
ExecStop=/usr/bin/podman stop \
	--ignore -t 10 \
	--cidfile=%t/%n.ctr-id
ExecStopPost=/usr/bin/podman rm \
	-f \
	--ignore -t 10 \
	--cidfile=%t/%n.ctr-id
Type=notify
NotifyAccess=all

[Install]
WantedBy=default.target
```

> Note: On newer versions the path is `/var/lib/postgresql`

Here you can see, that we are using the `/srv/postgresql` data directory (with a private SELinux label, that's the `Z`) and we are using version 15, which we want to upgrade/migrate to version 16.

For the migration the systemd service is stopped, and we are doing the above procedure on ephermal containers. After the migration is done, we will update the version tag to 16 and restart the service.

First we need to stop the systemd service and we also create a new directory for the version 16 database

    # systemctl stop postgresql-container
    # mkdir -p /srv/postgresql16/data

Now we export the data by running a new container. The database dump will be stored in the `dump` file, just as above

    # podman run --rm -itd -v /srv/postgresql/data:/var/lib/postgresql/data:Z --name postgresql15 docker.io/library/postgres:15
    # podman exec -t -u postgres postgresql15 pg_dumpall > dump

Check again the `dump` file for unwanted warnings.

Then we import the data and the configuration files into the new container. You might need to wait a bit after starting the container. I leave two blank lines as a reminder to be patient

    # podman run --rm -itd -e POSTGRES_PASSWORD=passw0rd -v /srv/postgresql16/data:/var/lib/postgresql/data:Z --name postgresql16 docker.io/library/postgres:16
    
    
    # podman exec -i -u postgres postgresql16 psql < dump
    # podman cp postgresql15:/var/lib/postgresql/data/pg_hba.conf postgresql16:/var/lib/postgresql/data/pg_hba.conf
    # podman cp postgresql15:/var/lib/postgresql/data/postgresql.conf postgresql16:/var/lib/postgresql/data/postgresql.conf

We can stop both containers now. I recommend to start the PostgreSQL16 container again to see if the configuration files are ok and ensure all databases (and tables and other entities) are present. We don't need the `POSTGRES_PASSWORD` after the database has been created.

    # podman stop postgresql15 postgresql16
    # podman run --rm -itd -v /srv/postgresql16/data:/var/lib/postgresql/data:Z --name postgresql16 docker.io/library/postgres:16
    # podman exec -ti -u postgres postgresql16 psql
    ...   # check if everying is ok
    # podman stop postgresql16

At this stage you will have the migrated database in `/srv/postgresql16/data` and the old one in `/srv/postgresql/data`. The next step is to rename the data directories

    # mv /srv/postgresql /srv/postgresql.old
    # mv /srv/postgresql16 /srv/postgresql

Now, update the systemd unit (Update the version tag `15` in the container image reference to `16`, i.e. `docker.io/library/postgres:16`) and restart the systemd unit.

    # vim /etc/systemd/system/postgresql-container.service
    # systemctl daemon-reload
    # systemctl restart postgresql-container.service

Congratulations, you should have successfully updates your PostgreSQL container to the next major version. In case you run into issues, the old data directory is still present.


# References

* https://www.postgresql.org/docs/16/upgrading.html


# Update

2025-09-29 - Note that on newer Postgresql version (18) the path changed from `/var/lib/postgresql/data` to `/var/lib/postgresql`.