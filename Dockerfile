FROM python:3.11.0-slim-bullseye
# Note that the python version needs to match that used to create
# poetry.lock.

MAINTAINER KBase Developer
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

# dockerize for config
RUN version=v0.17.0 && \
    wget -O - https://github.com/powerman/dockerize/releases/download/${version}/dockerize-`uname -s`-`uname -m` | install /dev/stdin /usr/local/bin/dockerize

# SSH for development
# RUN /etc/init.d/ssh start && /etc/init.d/ssh status

RUN mkdir -p /kb/module/work
RUN mkdir -p /kb/module/config
RUN chmod -R a+rw /kb/module
COPY ./src /kb/module/src
COPY ./scripts /kb/module/scripts
COPY ./templates /kb/module/templates
COPY ./poetry.lock /kb/module
COPY ./pyproject.toml /kb/module
COPY ./deploy.cfg /kb/module
COPY ./Makefile /kb/module
COPY ./kbase.yml /kb/module
COPY ./compile_report.json /kb/module

WORKDIR /kb/module

# RUN poetry lock
RUN poetry config virtualenvs.create false && poetry install

ENTRYPOINT [ "sh", "./scripts/entrypoint.sh" ]

CMD [ ]