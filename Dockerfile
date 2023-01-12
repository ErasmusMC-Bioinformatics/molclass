FROM mambaorg/micromamba:1.1.0 as base

ADD --chown=$MAMBA_USER:$MAMBA_USER requirements ./requirements

# copy requirements.txt to tmp, because that's where micromamba expects it for some reason...
RUN cp ./requirements/requirements.txt /tmp/requirements.txt && \
    micromamba install -y -n base -f requirements/environment.yml && \
    micromamba clean --all --yes

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG APP_HOME=/home/molclass/app
WORKDIR ${APP_HOME}

ADD --chown=$MAMBA_USER:$MAMBA_USER . ${APP_HOME}

ARG MAMBA_DOCKERFILE_ACTIVATE=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]