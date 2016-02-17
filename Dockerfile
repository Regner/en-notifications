

FROM debian:latest
MAINTAINER Regner Blok-Andersen <shadowdf@gmail.com>

RUN apt-get update -qq
RUN apt-get upgrade -y -qq
RUN apt-get install -y -qq python-dev python-pip
RUN pip install -qU pip

ENV GOOGLE_APPLICATION_CREDENTIALS "path-to-credentials.json"
ENV GCLOUD_DATASET_ID "your gce project"

ADD en_notifications.py /en_notifications/
ADD requirements.txt /en_notifications/

WORKDIR /en_notifications/

RUN pip install -r requirements.txt

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD python /en_notifications/en_notifications.py
