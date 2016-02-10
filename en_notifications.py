

import os
import logging

from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings                                                                                                                                        
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 10))
PULL_COUNT = int(os.environ.get('PULL_COUNT', 1))

# Datastore Settings
DS_CLIENT = datastore.Client()
SETTINGS_KIND = os.environ.get('DATASTORE_SETTINGS_KIND', 'EN-SETTINGS')

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()

SUBSCRIPTION = PS_TOPIC.subscription('en_notifications')


while True:
    logger.info('Polling for new notifications...')
    received = PS_SUBSCRIPTION.pull(max_messages=PULL_COUNT)
    ack_ids = []
    
    for message in received:
        try:
            logger.info('Got message ID {} with data {}.'.format(message[1].message_id, message[1].data))
            ack_ids.append(message[0])
        
        except:
            logger.info('Something went wrong with message ID {}.'.format(message[1].message_id))
    
    PS_SUBSCRIPTION.acknowledge(ack_ids)

    sleep(SLEEP_TIME)
