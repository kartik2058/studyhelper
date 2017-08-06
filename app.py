import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

users_interested_subjects = db.Table('users_interested_subjects', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id')))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    subjects = db.relationship('Subject', secondary=users_interested_subjects, backref='students', lazy='dynamic')


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def serialize(self):
        return {'id': self.id, 'name': self.name}


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
                existing_username = db.session.query(User).filter_by(username=username)
                if existing_username is None:
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

    return jsonify({'status': 'success', 'subjects': subjects_json})

@app.route('/subjects/new/', methods=['POST'])
def create_subject():
    name = request.form.get('name')
    if name is None:
        return jsonify({'status': 'error', 'error': 'Subject name not defined.'})
    else:
        if not name.strip():
            return jsonify({'status': 'error', 'error': 'Subject name cannot be empty.'})

    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify({'status': 'success', 'subject_id': subject.id})

if __name__ == '__main__':
    app.run()