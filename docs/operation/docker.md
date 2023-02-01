# Docker Usage

> to do
> 
This project uses docker for most tasks. The reason is simple. It reduces the number of host dependencies, making the startup effort to work on projects faster and more deterministic.

There are four docker compose files for running the service:

- docker-compose-dev.yml provides the development container




| name | volume mount source | reload on change | mongodb | mongo express |
|---|---|---|---|---|
| docker-compose-dev.yml | yes | yes | yes | yes |
| docker-compose-testing.yml | yes | no | yes | no |
| docker-compose-prod-like.yml | no | no | yes | no |
| docker-compose-runner.yml | yes | no | no | no |
