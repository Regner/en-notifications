

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


def format_notification(title, subtitle, url, extra_text):
    notification = {
        'notification': {
            'title': title,
            'subtitle': subtitle,
        }
    }
    
    if url is not None:
        notification['notification']['url'] = url
        
    if extra_text is not None:
        notification['notification']['extra_text'] = extra_text
    
    return notification


def format_gcm_kwargs(notification, topic, collapse_key):
    gcm_kwargs = {
        'data': notification,
        'topic': topic,
    }
    
    if collapse_key is not None:
        gcm_kwargs['collapse_key'] = collapse_key
    
    return gcm_kwargs


while True:
    logger.info('Polling for new notifications...')
    received = PS_SUBSCRIPTION.pull(max_messages=PULL_COUNT)
    sleep_time = DEFAULT_SLEEP_TIME
    ack_ids = []
    
    for message in received:
        logger.info('Got message ID {} with attributes {}.'.format(message[1].message_id, message[1].attributes))
        
        url = message[1].attributes.get('url', None)
        extra_text = message[1].attributes.get('extra_text', None)
        collapse_key = message[1].attributes.get('collapse_key', None)
        title = message[1].attributes['title']
        subtitle = message[1].attributes['subtitle']
        service = message[1].attributes['service']
        topic =  message[1].attributes['topic']
        
        notification = format_notification(title, subtitle, url, extra_text)
        gcm_kwargs = format_gcm_kwargs(notification, topic, collapse_key)

        logger.info('Sending message to the following topic "/topics/{}"'.format(topic))
        
        response = GCM_CLIENT.send_topic_message(**gcm_kwargs)
        
        ack_ids.append(message[0])
    
    if len(ack_ids) > 0:
        PS_SUBSCRIPTION.acknowledge(ack_ids)
        sleep_time = 0
    
    sleep(sleep_time)
