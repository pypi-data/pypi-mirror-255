"""
Chat app for LitenAI
"""
import sys
import panel as pn

import litenai as tenai

def health_app():
    """
    Health app for LitenAI
    """
    return 'OK'

config = tenai.Config()

def litenai_chat_app():
    """
    Chat app for LitenAI
    """
    session = tenai.Session.get_or_create('chatsession', config)
    chatbot = tenai.ChatBot(session=session)
    chat_panel_column = chatbot.get_column()
    chat_panel_column.servable(title="LitenAI")
    return chat_panel_column




def print_usage():
    """
    Print usage
    """
    print(f"""
Usage: python litenchat.py
Example: python litenchat.py
Received: f{sys.argv}
""")

app_routes = {
    'health': health_app,
    'litenchat': litenai_chat_app
}

pn.extension('bokeh')
port = int(config.get_config(tenai.Config.LITEN_SERVER_PORT))
pn.serve(app_routes, port=port, show=False)
