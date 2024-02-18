"""
Flask routes for liten API.
To start the Flask server do the following -
flask --app=litenapp.py run
"""
import os

import litenai as tenai

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/create/<session_name>")
def create_session(session_name):
    """
    create a session with the given session_name. Liten yaml config file can be specified as 
    an env variable LITEN_CONFIG_FILE. If creating these default config values are used. See the sample
    config file for environment variable.
    When making a session call, the env variables can be passed as args to override the config file.
    OpenAI API key to for API calls
    "OPENAI_API_KEY" : "<insert your litenkey here>"
    Spark local IP where  master is running. If local do local[1] or 
    "SPARK_MASTER_URL" : "local[2]"
    Liten Datalake URL - assumes litenlakehouse.py is here for file scheme
    "LITEN_LAKEHOUSE_URL": "file:///content/samplelogfiles/"
    Pass them as args to override these.
    Example:
    http://127.0.0.1:5000/create/test?LITEN_LAKEHOUSE_URL=file:/home/hkverma/work/samplelogfiles&OPENAI_API_KEY=sk-xxxxxxx&SPARK_MASTER_URL=local[2]
    """
    return tenai.LitenAPI.create_session(session_name, request.args.to_dict())

@app.route("/get/<session_name>")
def get_session(session_name):
    """
    get a session with the given session_name.
    """
    return tenai.LitenAPI.create_session(session_name, request.args.to_dict())

@app.route("/append/<session_name>/<prompt>")
def append_user_message(session_name, prompt):
    """
    get a session with the given session_name
    If creating use the config file_name
    """
    return tenai.LitenAPI.append_user_message(session_name, prompt)


@app.route("/ask/<session_name>/<prompt>")
def ask_liten(session_name, prompt):
    """
    Ask to complete prompt for session_name
    Example:
    http://127.0.0.1:5000/ask/test/%22What%20are%20status%20code%20errors%22
    """
    return tenai.LitenAPI.ask(session_name, prompt)

@app.route("/send/<session_name>/<prompt>")
def send_liten(session_name, prompt):
    """
    Send to complete prompt for session_name. Master agent identifies the action from the prompt and completes it using the appropriate agent.
    Example:
    http://127.0.0.1:5000/send/xxx/%22Generate%20sql%20for%20the%20following.%20Select%20top%20100%20rows.%22
    """
    return tenai.LitenAPI.send(session_name, prompt)