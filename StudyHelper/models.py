from StudyHelper import db
import datetime

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
