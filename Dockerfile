FROM python:3.11.1-slim-bullseye
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

# We need curl to install poetry; git for the git-info tool.
RUN apt-get update && apt-get install -y curl git

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.3.0

# Don't need curl any more.
RUN apt-get purge -y curl && apt-get autoremove -y

# Annoyingly it puts it here.
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/kb/module/src"

RUN mkdir -p /kb/module/work && mkdir /kb/module/config && chmod -R a+rw /kb/module

# Copying only files needed for service runtime.
# Other usages of this image, e.g. testing, mount the project root at /kb/module
# and have access to everything.
COPY ./scripts /kb/module/scripts
COPY ./src/orcidlink /kb/module/src/orcidlink
COPY ./etc /kb/module/etc
COPY ./poetry.lock /kb/module
COPY ./pyproject.toml /kb/module
COPY ./SERVICE_DESCRIPTION.toml /kb/module

WORKDIR /kb/module

RUN poetry config virtualenvs.create false && poetry install

ENTRYPOINT [ "scripts/entrypoint.sh" ]

CMD [ "scripts/start-server.sh" ]