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

SHELL ["conda", "run", "--no-capture-output", "-n", "molclass", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "molclass", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]