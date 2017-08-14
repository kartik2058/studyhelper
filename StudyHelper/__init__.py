import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)


def make_error(error_message, error_code, extra_key=None, extra_value=None):
    if extra_key is not None and extra_value is not None:
        return jsonify({'status': 'error', 'error_code': error_code, 'error_message': error_message, extra_key: extra_value})
    else:
        return jsonify(
            {'status': 'error', 'error_code': error_code, 'error_message': error_message})


@app.route('/')
def home():
    return "<h1>Welcome to StudyHelper API Server!</h1><h2>I made this server using Python (Flask) for my StudyHelper app hope you enjoy using my app.</h2><h3>Contact me at: kartik2058@gmail.com</h3>"

from StudyHelper.users import users_module
from StudyHelper.subjects import subjects_module
from StudyHelper.questions import questions_module
from StudyHelper.answers import answers_module
from StudyHelper.chats import chats_module
from StudyHelper.messages import messages_module

app.register_blueprint(users_module, url_prefix='/users')
app.register_blueprint(subjects_module, url_prefix='/subjects')
app.register_blueprint(questions_module, url_prefix='/questions')
app.register_blueprint(answers_module, url_prefix='/questions/<int:question_id>/answers')
app.register_blueprint(chats_module, url_prefix='/chats')
app.register_blueprint(messages_module, url_prefix='/chats/<int:chat_id>/messages')