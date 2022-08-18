FROM condaforge/mambaforge:4.12.0-2 as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements .
RUN mamba env create -f environment.yml

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

COPY . ${APP_HOME}
RUN ln -s ${APP_HOME}/compose/molclass/start ${APP_HOME}/start && chmod 0777 ./start

ENTRYPOINT ["./start"]