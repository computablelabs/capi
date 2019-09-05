FROM python:3.6-stretch

COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

ENV PYTHONPATH := .
ENV ENV_CONFIG_FILE=/app/config/development.py

CMD ["python", "run.py"]
