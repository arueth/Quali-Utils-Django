###############################################################################
# BUILD
###############################################################################
FROM python:3.6.1-alpine as builder

RUN apk update \
&& apk add gcc musl-dev postgresql-dev \
&& rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY app/requirements.txt ./

RUN pip install -r requirements.txt





###############################################################################
# FINAL
###############################################################################
FROM python:3.6.1-alpine

COPY --from=builder /usr/local/lib/python3.6/site-packages/ /usr/local/lib/python3.6/site-packages/

RUN apk update \
&& apk add postgresql \
&& rm -rf /var/cache/apk/*

COPY app/ ./

COPY docker-entrypoint.sh /

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
