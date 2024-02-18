"""
Starts slack app for Liten and handles events.
"""

import uuid
import requests

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import litenai as tenai

config = tenai.Config()
tlogger = config.logger.logger()

app = App(token = tenai.SlackMessage.bot_token)

# can be used with file_shared event, currently handled in message event
@app.event("file_shared")
def handle_file_shared_events(body, logger=tlogger):
    """ 
    Handles the file_shared event
    """
    logger.info(f"Event file_shared: {body}")

@app.event("app_mention")
def handle_app_mention_events(body, say, logger=tlogger):
    """ 
    Handles the app-mention event. Create a new session if one does not exist.
    """
    try:
        logger.info(f"Event app_mention: {body}")
        msg = tenai.SlackMessage(body=body,
                                 app=app)
        if msg.text:
            say(text=msg.reply_message(), thread_ts = msg.ts())
    except Exception as e:
        logger.error(f"Event app_mention: Error'{e}' for message body: {body}")
        say(text="Error reading message", thread_ts = msg.ts())

@app.event("message")
def handle_message_events(body, logger=tlogger):
    """ 
    Handles the message event
    """
    try:
        logger.info(f"Event message: {body}")
        msg = tenai.SlackMessage(body=body,
                                 app=app)
        # If files are shared, read it
        # Reply only if prompt provided by the user
        # if subtype is file_share read the file
        if 'subtype' in msg.event.keys() and msg.event['subtype'] == "file_share":
            response = msg.read_files()
            app.client.chat_postMessage(channel=msg.channel(), text=response)
        if msg.text:
            # Ignore if Liten is mentioned, app_mention event should handle it
            if not msg.if_liten_mentioned():
                if msg.channel_type() == "im":
                    response = msg.reply_message()
                    app.client.chat_postMessage(channel=msg.channel(), text=response)
                else:
                    msg.append_message()
    except Exception as exc:
        logger.error(f"Event message: Error '{exc}' for body: {body}")
        app.client.chat_postMessage(channel=msg.channel(), text="Error reading message")

@app.event("app_home_opened")
def handle_app_home_opened_events(body, logger=tlogger):
    """ 
    Handles the app_home_opened event
    """
    logger.info(f"App Event app_home_opened: {body}")

if __name__ == "__main__":
    handler = SocketModeHandler(app=app, 
                                app_token=tenai.SlackMessage.app_token,
                                logger=tlogger)
    handler.start()