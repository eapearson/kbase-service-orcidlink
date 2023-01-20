FROM python:3.11.0-slim-bullseye
# Note that the python version needs to match that used to create
# poetry.lock.

MAINTAINER KBase Developer
LABEL org.opencontainers.image.source = "https://github.com/eapearson/kbase-service-orcidlink"
LABEL org.opencontainers.image.description="A KBase core service to provide for linking a KBase account to an ORCID account, and associated services"
LABEL org.opencontainers.image.licenses=MIT

# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.
# -----------------------------------------

RUN apt update && apt install -y curl wget 

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
# Annoyingly it puts it here.
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/kb/module/src"

RUN mkdir -p /kb/module/work
RUN mkdir -p /kb/module/config
RUN chmod -R a+rw /kb/module

# Copying only files needed for service runtime.
# Other usages of this image, e.g. testing, mount the project root at /kb/module
# and have access to everything.
COPY ./scripts /kb/module/scripts
COPY ./src /kb/module/src
COPY ./templates /kb/module/templates
COPY ./poetry.lock /kb/module
COPY ./pyproject.toml /kb/module
COPY ./deploy.cfg /kb/module
COPY ./kbase.yml /kb/module

WORKDIR /kb/module

RUN poetry config virtualenvs.create false && poetry install

ENTRYPOINT [ "scripts/entrypoint.sh" ]

CMD [ "scripts/run-server.sh" ]