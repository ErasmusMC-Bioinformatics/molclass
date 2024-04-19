FROM python:3.10.9-slim as builder

RUN apt-get update && \
    apt-get install git gcc g++ -y && \
    apt-get clean

COPY requirements/requirements.txt /app/requirements.txt

RUN pip install --user -r /app/requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

FROM python:3.10.9-slim as app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/ /app/
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8080
