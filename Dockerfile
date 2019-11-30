FROM python:3.7-alpine3.9

WORKDIR /usr/app

ENV HEALTH_LOG_SERVER_HOST 0.0.0.0
ENV HEALTH_LOG_SERVER_PORT 80

COPY setup.py .

RUN apk update \
    && apk add -U --no-cache \
    --repository http://dl-5.alpinelinux.org/alpine/edge/main/ \
    --repository http://dl-5.alpinelinux.org/alpine/edge/testing/ \
    # OS deps for psycopg2
    libpq \
    && apk add -U --no-cache \
    --repository http://dl-5.alpinelinux.org/alpine/edge/main/ \
    --repository http://dl-5.alpinelinux.org/alpine/edge/testing/ \
    -t build-deps \
    # OS build deps for psycopg2
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install -e . \
    && apk del --no-cache build-deps

COPY healthlog ./healthlog
ENTRYPOINT ["healthlog"]
