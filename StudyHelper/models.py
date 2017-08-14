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
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def serialize(self):
        json_subjects = []
        for subject in self.subjects:
            json_subjects.append(subject.serialize())
        if not json_subjects:
            return {'id': self.id, 'username': self.username, 'points': self.points, 'subjects': None}
        return {'id': self.id, 'username': self.username, 'points': self.points, 'subjects': json_subjects}


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
    title = db.Column(db.String, nullable=False)
    question = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def serialize(self):
        return {'id': self.id, 'title': self.title, 'question': self.question, 'posted_on': self.posted_on, 'updated_on': self.updated_on, 'asked_by': self.user.username, 'subject': self.subject.name}


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    answer = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def serialize(self):
        return {'id': self.id, 'answer': self.answer, 'posted_on': self.posted_on, 'updated_on': self.updated_on, 'answered_by': self.user.username, 'question_id': self.question_id}


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)

    users = db.relationship('User', secondary=chat_members, backref='chats', lazy='dynamic')
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade='all, delete-orphan')

    def serialize(self):
        users_json = []
        for user in self.users:
            users_json.append(user.id)
        if not users_json:
            return {'id': self.id, 'question': self.question}

        return {'id': self.id, 'question': self.question, 'chat_members': users_json}


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    message = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def serialize(self):
        return {'id': self.id, 'message': self.message, 'posted_on': self.posted_on, 'chat': self.chat_id, 'posted_by': self.user_id}
