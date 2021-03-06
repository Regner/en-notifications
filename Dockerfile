

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

ENV GCM_API_KEY "GCM API Key"

ADD en_notifications.py /en_notifications/
ADD requirements.txt /en_notifications/
ADD docker-entrypoint.sh /docker-entrypoint.sh

WORKDIR /en_notifications/

RUN apt-get update -qq \
&& apt-get upgrade -y -qq \
&& apt-get install -y -qq python-dev python-pip \
&& apt-get autoremove -y \
&& apt-get clean autoclean \
&& pip install -qU pip \
&& pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD gunicorn en_notifications:app -w 1 -b 0.0.0.0:8000 --log-level info --timeout 120 --pid /en_notifications/en_notifications.pid
