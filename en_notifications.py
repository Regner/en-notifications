

import os
import json
import logging
import requests

from gcm import GCM
from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings                                                                                                                                        
DEFAULT_SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 60))
PULL_COUNT = int(os.environ.get('PULL_COUNT', 1))

# GCM Settings
GCM_CLIENT = GCM(os.environ.get('GCM_API_KEY'))

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()

PS_SUBSCRIPTION = PS_TOPIC.subscription('en_notifications')

if not PS_SUBSCRIPTION.exists():
    PS_SUBSCRIPTION.create()


while True:
    logger.info('Polling for new notifications...')
    received = PS_SUBSCRIPTION.pull(max_messages=PULL_COUNT)
    sleep_time = DEFAULT_SLEEP_TIME
    ack_ids = []
    
    for message in received:
        logger.info('Got message ID {} with attributes {}.'.format(message[1].message_id, message[1].attributes))
        
        url = message[1].attributes['url']
        title = message[1].attributes['title']
        subtitle = message[1].attributes['subtitle']
        service = message[1].attributes['service']
        topics = json.loads(message[1].attributes['topics'])
        
        notification = {
            'title': title,
            'subtitle': subtitle,
            'url': url,
        }
        
        for topic in topics:
            logger.info('Sending message to the following topic {}'.format(len(topic)))
            
            response = GCM_CLIENT.send_topic_message(
                data=notification,
                topic=topic,
            )
        
        ack_ids.append(message[0])
    
    if len(ack_ids) > 0:
        PS_SUBSCRIPTION.acknowledge(ack_ids)
        sleep_time = 0
    
    sleep(sleep_time)
