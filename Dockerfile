FROM python:3-alpine3.12

RUN apk add --update alpine-sdk glib-dev

WORKDIR /usr/src/igrill

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
VOLUME /usr/src/igrill/config

CMD [ "python", "./monitor.py", "-c", "/usr/src/igrill/config" ]
