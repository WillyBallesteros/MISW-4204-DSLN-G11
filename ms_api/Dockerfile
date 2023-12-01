FROM python:3.8-alpine

RUN apk add --no-cache

RUN pip install gunicorn

WORKDIR /app

COPY . .

RUN apk add --no-cache build-base && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base

CMD gunicorn -w 1 -t 60 app:app --bind 0.0.0.0:$PORT
