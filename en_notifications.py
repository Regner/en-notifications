

import os
import json
import logging

from gcm import GCM
from flask import Flask, request


app = Flask(__name__)

# App Settings
app.config['BUNDLE_ERRORS'] = True

# GCM Settings
GCM_CLIENT = GCM(os.environ.get('GCM_API_KEY'))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)


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


@app.route('/external/', methods=['POST'])
def message():
    message = request.json
    
    app.logger.info('Got a new message {}.'.format(message))

    # url = message['attributes'].get('url', None)
    # extra_text = message['attributes'].get('extra_text', None)
    # collapse_key = message['attributes'].get('collapse_key', None)
    # title = message['attributes']['title']
    # subtitle = message['attributes']['subtitle']
    # service = message['attributes']['service']
    # topic =  message['attributes']['topic']
    
    # notification = format_notification(title, subtitle, url, extra_text)
    # gcm_kwargs = format_gcm_kwargs(notification, topic, collapse_key)

    # app.logger.info('Sending message to the following topic "/topics/{}"'.format(topic))
    
    # response = GCM_CLIENT.send_topic_message(**gcm_kwargs)

    return ''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
