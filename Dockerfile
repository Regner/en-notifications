

FROM debian:jessie
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

RUN \
	apt-get update -qq \
	&& apt-get upgrade -y -qq \
	&& apt-get install -y -qq python-dev python-pip \
	&& pip install -qU pip \
	&& apt-get autoremove -y \
	&& apt-get clean autoclean

ENV GOOGLE_APPLICATION_CREDENTIALS "path-to-credentials.json"
ENV GCLOUD_DATASET_ID "your gce project"

ADD en_notifications.py /en_notifications/
ADD requirements.txt /en_notifications/
ADD docker-entrypoint.sh /docker-entrypoint.sh

WORKDIR /en_notifications/

RUN pip install -r requirements.txt

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD python /en_notifications/en_notifications.py
