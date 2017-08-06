import os
import re
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

subjects_interested_in = db.Table('subjects_interested_in', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id')))
chat_members = db.Table('chat_members', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('chat_id', db.Integer, db.ForeignKey('chats.id')))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    subjects = db.relationship('Subject', secondary=subjects_interested_in, backref='students', lazy='dynamic')
    questions = db.relationship('Question', backref='user', lazy='dynamic')
    answers = db.relationship('Answer', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='user', lazy='dynamic')


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    questions = db.relationship('Question', backref='subject', lazy='dynamic', cascade='all, delete-orphan')

    def serialize(self):
        return {'id': self.id, 'name': self.name}


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    answer = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_suggested = db.Column(db.Boolean, default=False, nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='answer', lazy='dynamic', cascade='all, delete-orphan')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    users = db.relationship('Chat', secondary=chat_members, backref='chats', lazy='dynamic')
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade='all, delete-orphan')


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    message = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@app.route('/')
def home():
    return "<h1>Welcome to StudyHelper API Server!</h1><h2>I made this server using Python (Flask) for my StudyHelper app hope you enjoy using my app.</h2><h3>Contact me at: kartik2058@gmail.com</h3>"


@app.route('/join/', methods=['POST'])
def join():
    errors = {}

    username = request.form.get('username')
    if username is not None:
        if not username.strip():
            errors['username'] = 'Username field cannot be empty.'
        else:
            if len(username) <= 3:
                errors['username'] = 'Username should be greater then 3.'
            elif len(username) >= 20:
                errors['username'] = 'Username should be less then 20 characters.'
            else:
                existing_username = db.session.query(User).filter_by(username=username).first()
                if existing_username is not None:
                    errors['username'] = 'Username is already taken, please try another username.'
    else:
        errors['username'] = 'Username not defined.'

    password = request.form.get('password')
    if password is not None:
        if not password.strip():
            errors['password'] = 'Password field cannot be empty.'
        else:
            if len(password) <= 5:
                errors['password'] = 'Password should be greater then 5 characters.'
            elif not re.search(r'\d', password):
                errors['password'] = 'Password should contain numbers.'
    else:
        errors['password'] = 'Password not defined.'

    interested_subjects = request.form.get('interested_subjects')
    if interested_subjects is None:
        errors['interested_subjects'] = 'Interested Subjects not defined.'
    else:
        interested_subjects = [int(x) for x in re.compile("^\s+|\s*,\s*|\s+$").split(interested_subjects) if x]

    if errors:
        return jsonify({'status': 'error', 'errors': errors})
    else:
        password = generate_password_hash(password)
        new_user = User(username=username, password=password)
        db.session.add(new_user)

        for subject in interested_subjects:
            subject = db.session.query(Subject).get(subject)
            if subject is not None:
                subject.students.append(new_user)

        db.session.commit()

        return jsonify({'status': 'success', 'user_id': new_user.id})


@app.route('/login/', methods=['POST'])
def login():
    errors = {}

    username = request.form.get('username')
    if username is None:
        return jsonify({'status': 'error', 'error': 'Username not defined.'})

    password = request.form.get('password')
    if password is None:
        return jsonify({'status': 'error', 'error': 'Password not  defined.'})

    if not username.strip() and not password.strip():
        return jsonify({'status': 'error', 'error': 'Please enter your username and password.'})
    elif not username.strip():
        return jsonify({'status': 'error', 'error': 'Please enter your username.'})
    elif not password.strip():
        return jsonify({'status': 'error', 'error': 'Please enter your password.'})

    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        if check_password_hash(user.password, password):
            return jsonify({'status': 'success', 'authentication': 'You have been logged in successfully.'})
        else:
            return jsonify({'status': 'error', 'error': 'Username and Password does not match.'})
    else:
        return jsonify({'status': 'error', 'error': 'Username and Password does not match.'})


@app.route('/subjects/', methods=['GET'])
def get_subjects():
    subjects = db.session.query(Subject).all()
    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    if not subjects_json:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    return jsonify({'status': 'success', 'subjects': subjects_json})


@app.route('/subjects/<int:subject_id>/', methods=['GET'])
def get_subject(subject_id):
    subject = db.session.query(Subject).get(int(subject_id))

    if subject is None:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    return jsonify({'status': 'success', 'subject': subject.serialize()})


@app.route('/subjects/search/<string:subject_name>/', methods=['GET'])
def search_subjects(subject_name):
    subjects = db.session.query(Subject).filter(Subject.name.like(subject_name+'%')).all()

    if not subjects:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    return jsonify({'status': 'success', 'subjects': subjects_json})


@app.route('/subjects/new/', methods=['POST'])
def create_subject():
    name = request.form.get('name')
    if name is None:
        return jsonify({'status': 'error', 'error': 'Subject name not defined.'})
    else:
        if not name.strip():
            return jsonify({'status': 'error', 'error': 'Subject name cannot be empty.'})

    existing_subject = db.session.query(Subject).filter_by(name=name).first()
    if existing_subject is not None:
        return jsonify({'status': 'error', 'error': name + ' is already present.',
                        'existing_subject_id': existing_subject.id})

    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify({'status': 'success', 'subject_id': subject.id})

if __name__ == '__main__':
    app.run()