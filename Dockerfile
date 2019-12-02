FROM python:3.6-stretch

ARG network

COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install -i https://test.pypi.org/simple/ computable

ENV PYTHONPATH := .
ENV ENV_CONFIG_FILE=/app/config/${network}.py

CMD ["/app/scripts/launch.sh"]
