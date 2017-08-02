from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return "<h1>Welcome to StudyHelper!</h1>\n<h2>Here is my personal email address kartik2058@gmail.com</h2>"


if __name__ == '__main__':
    app.run()