FROM python:3.8-alpine

RUN apk add --no-cache nginx
RUN pip install gunicorn

COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /app

COPY . .

RUN apk add --no-cache build-base && \
    apk add --no-cache postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "app:app", "--bind", "0.0.0.0:5000"]
