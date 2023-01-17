# ORCIDLink

This is a prototype service for linking a KBase account to an ORCID account. 

Although it works with kb-sdk and is compatible with the KBase service wizard app runner, it does not use most of the machinery. Rather it is a simple fastapi-based service.



## Usage

```shell
ORCID_SANDBOX_CLIENT_ID=<client id> ORCID_SANDBOX_CLIENT_SECRET=<client secret> docker compose up
```

It currently works with the ORCID sandbox, so the credentials used above must be obtained from an ORCID sandbox account.

## Development

### build image
```shell
docker compose build
```

### shell into image to inspect
```shell
docker compose run --entrypoint sh orcidlink
```  

### run it
```shell
docker compose up
```

## Development 2

This workflow works well with pycharm:

> Had to set up poetry to work without a virtual env; although it worked once, 
> for some reason I couldn't set the interpreter within the virtualenv.

- create new interpreter for docker compose

- make sure the environment variables are set, you can copy paste the following:
```text
KBASE_ENDPOINT=https://ci.kbase.us/services/;KBASE_SECURE_CONFIG_PARAM_ORCID_CLIENT_ID={{OMITTED}} ;KBASE_SECURE_CONFIG_PARAM_ORCID_CLIENT_SECRET={{OMITTED}}
```

- make sure interpreter paths are set:
```text
/usr/local/lib/python3.11/site-packages  (added by user)
/kb/module/src  (added by user)
/usr/local/lib/python3.11  (added by user)
/usr/local/lib/python3.11/lib-dynload
/root/.local/lib/python3.11/site-packages
```

- make sure the interpreter is:

```text
/usr/local/bin/python3.11
```

if in doubt shell into the container (using start-dev-bash.sh) and issue

```shell
poetry env info
```



## Testing

- shell into container
- run `pytest --cov src --cov-report=html src`
