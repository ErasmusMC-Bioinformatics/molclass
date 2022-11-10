FROM condaforge/mambaforge:4.12.0-2 as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ADD requirements ./requirements
RUN mamba env create -f requirements/environment.yml

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

COPY . ${APP_HOME}
