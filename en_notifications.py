

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
EN_GCM_URL = os.environ.get('EN_GCM_URL', 'http://en-gcm:8000/internal/')

# GCM Settings
GCM_CLIENT = GCM(os.environ.get('GCM_API_KEY'))

# Datastore Settings
DS_CLIENT = datastore.Client()
SETTINGS_KIND = os.environ.get('DATASTORE_SETTINGS_KIND', 'EN-SETTINGS')

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()

PS_SUBSCRIPTION = PS_TOPIC.subscription('en_notifications')

if not PS_SUBSCRIPTION.exists():
    PS_SUBSCRIPTION.create()


def get_tokens_from_char_ids(character_ids):
    params = {'character_ids': ','.join([str(x) for x in character_ids])}
    response = requests.get(EN_GCM_URL, params=params)
    response.raise_for_status()
    
    return response.json()


while True:
    logger.info('Polling for new notifications...')
    received = PS_SUBSCRIPTION.pull(max_messages=PULL_COUNT)
    sleep_time = DEFAULT_SLEEP_TIME
    ack_ids = []
    
    for message in received:
        logger.info('Got message ID {} with data {}.'.format(message[1].message_id, message[1].data))
        
        title = message[1].data
        url = message[1].attributes['url']
        feed_name = message[1].attributes['feed_name']
        service = message[1].attributes['service']
        collapse_key = message[1].attributes['collapse_key']
        character_ids = json.loads(message[1].attributes['character_ids'])
        
        tokens = get_tokens_from_char_ids(character_ids)
        
        notification = {
            'title': title,
            'url': url,
            'feed_name': feed_name,
        }
        
        logger.info('Sending message to {} tokens.'.format(len(tokens)))
        
        response = GCM.json_request(
            registration_ids=tokens,
            data=notification,
            collapse_key=collapse_key,
        )
        
        # Update registration IDs
        # Remove registration IDs
        
        ack_ids.append(message[0])
    
    if len(ack_ids) > 0:
        PS_SUBSCRIPTION.acknowledge(ack_ids)
        sleep_time = 0
    
    sleep(sleep_time)
