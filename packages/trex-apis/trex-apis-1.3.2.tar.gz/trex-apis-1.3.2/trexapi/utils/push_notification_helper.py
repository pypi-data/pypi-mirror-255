'''
Created on 30 Jan 2024

@author: jacklok
'''
from firebase_admin import credentials, messaging

def create_prepaid_push_notification(title_data=None, speech=None, message_data=None, device_token=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data={
            'speech': speech,
        },
        token=device_token,
    )
    
    messaging.send(message)
