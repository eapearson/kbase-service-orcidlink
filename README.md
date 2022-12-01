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
