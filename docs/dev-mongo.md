>
> This document was stolen from the jgi_gateway service.
>

# Development

## install mongo image

(1) Use Kitematic to get the latest in the 3 series (currently 3.6.9) - the 2 series which KBase uses is not supported in the official distribution.

(2) Change image settings:

**Settings > General**

Add the environment variables:

| KEY                        | VALUE    |
| -------------------------- | -------- |
| MONGO_INITDB_ROOT_USERNAME | dev_root |
| MONGO_INITDB_ROOT_PASSWORD | dev_r00t |
|                            |          |

Click the `SAVE` button.

**Settings > Volumes**

For each DOCKER FOLDER set the LOCAL FOLDER

| DOCKER FOLDER  | LOCAL FOLDER          |
| -------------- | --------------------- |
| /data/db       | SPRINT/mongo/db       |
| /data/configdb | SPRINT/mongo/configdb |
|                |                       |

> where SPRINT is your sprint or working directory

**Settings > Network**

Enable the `kbase-dev` network if it is available, then click the `SAVE` button.

> If the `kbase-dev` network is not available, you should start the kbase-ui development image first in order to establish the kbase-dev network, or simply issue `docker network create kbase-dev`.

(3) Stop the container, then clear the database directories

    rm -rf SPRINT/mongo/*

then start the container.

This is required because the root user image settings only take effect when the container is first created, and it is automatically created when you add the image through Kitematic.

(4) Add jgi_gateway user and database

now log in from the command line (host) as the root user

```
mongo --host localhost --port PORT --username dev_root --password dev_r00t admin
```

> Where PORT is the port assigned to mongo by Docker. See **PUBLISHED IP:PORT** in the **Settings > Hostname/Ports** tab.

> If you don't have mongo installed locally, use your favorite method for doing this. E.g. `sudo port install mongodb` to install with macports (my favorite).

Now create a user with read/write permissions

```
> use jgi_gateway
> db.createUser({user: "jgi_gateway", pwd: "jgi_gateway", passwordDigestor: "server", roles: [{role: "readWrite", db: "jgi_gateway"}]})
```

These settings will match the defaults for the UIService development configuration used in `scripts/run-docker-image-dev.sh`

## FIN

You are now ready to hack on jgi_gateway and use it directly from kbase-ui using the dynamic-services option.

E.g.

in jgi_gateway

```
make docker-image-dev
make run-docker-image-dev
```

in kbase-ui

```
make dev-start dynamic-services="jgi_gateway"
```

> At the moment you also need to make a uncomment the service in config/services.yml and rebuild kbase-ui, but that step will disappear soon.