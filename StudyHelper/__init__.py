import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

@app.route('/')
def home():
    return "<h1>Welcome to StudyHelper API Server!</h1><h2>I made this server using Python (Flask) for my StudyHelper app hope you enjoy using my app.</h2><h3>Contact me at: kartik2058@gmail.com</h3>"

from users import users_module
from subjects import subjects_module

app.register_blueprint(users_module, url_prefix='/users')
app.register_blueprint(subjects_module, url_prefix='/subjects')
