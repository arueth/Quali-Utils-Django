FROM python:2.7.13-alpine

RUN apk update \
&& apk upgrade \
&& rm -rf /var/cache/apk/* \
&& pip install -U pip

WORKDIR /usr/src/app

COPY app/requirements.txt ./

RUN pip install -r requirements.txt

COPY app/ ./

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
