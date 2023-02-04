FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED 1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends ffmpeg

WORKDIR /service

COPY . .

RUN python -m venv venv
RUN . ./venv/bin/activate && pip install -r requirements.txt && pip install uvicorn gunicorn

CMD . ./venv/bin/activate && gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.service:app
