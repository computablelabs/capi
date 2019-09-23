FROM python:3.6-stretch

ARG accesskey
ARG secretkey

COPY . /app
WORKDIR /app

ENV AWS_ACCESS_KEY_ID=$accesskey
ENV AWS_SECRET_ACCESS_KEY=$secretkey

RUN pip install -r requirements.txt

ENV PYTHONPATH := .
ENV ENV_CONFIG_FILE=/app/config/staging.py

CMD ["/app/scripts/launch.sh"]
