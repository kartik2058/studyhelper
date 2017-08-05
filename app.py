import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

users_interests = db.Table('users_interests', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('interest_id', db.Integer, db.ForeignKey('interests.id')))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    interests = db.relationship('Interest', secondary=users_interests, backref='students', lazy='dynamic')


class Interest(db.Model):
    __tablename__ = 'interests'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    interest = db.Column(db.String(120), unique=True, nullable=False)

    def serialize(self):
        return {'id': self.id, 'name': self.interest}


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

    interests = request.form.get('interests')
    if interests is None:
        errors['interests'] = 'Interests not defined.'
    else:
        interests = [int(x) for x in re.compile("^\s+|\s*,\s*|\s+$").split(interests) if x]

    if errors:
        return jsonify({'status': 'error', 'errors': errors})
    else:
        password = generate_password_hash(password)
        new_user = User(username=username, password=password)
        db.session.add(new_user)

        for interest in interests:
            interest = db.session.query(Interest).get(interest)
            if interest is not None:
                interest.students.append(new_user)

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


@app.route('/get_interests/', methods=['GET'])
def get_interests():
    interests = db.session.query(Interest).all()
    json_interests = []
    for interest in interests:
        json_interests.append(interest.serialize())

    return jsonify({'status': 'success', 'interests': json_interests})


if __name__ == '__main__':
    app.run()