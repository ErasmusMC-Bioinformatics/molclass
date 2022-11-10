FROM condaforge/mambaforge:4.12.0-2 as base

RUN useradd --create-home --shell /bin/bash molclass
USER molclass
WORKDIR /home/molclass

ADD --chown=molclass:molclass requirements ./requirements
RUN mamba env create -f requirements/environment.yml

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG APP_HOME=/home/molclass/app
WORKDIR ${APP_HOME}

ADD --chown=molclass:molclass . ${APP_HOME}
