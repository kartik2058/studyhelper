from flask import request, jsonify, Blueprint
from StudyHelper.models import db, User, Subject
from StudyHelper import make_error
import re
from werkzeug.security import generate_password_hash, check_password_hash

users_module = Blueprint('users', __name__)


@users_module.route('/signup/', methods=['POST'])
@users_module.route('/signup', methods=['POST'])
def signup():
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

    subjects_interested_in = request.form.get('subjects_interested_in')
    if subjects_interested_in is None:
        errors['subjects_interested_in'] = 'Interested Subjects not defined.'
    else:
        subjects_interested_in = [int(x) for x in re.compile("^\s+|\s*,\s*|\s+$").split(subjects_interested_in) if x]

    if errors:
        return jsonify({'status': 'error', 'errors': errors})
    else:
        password = generate_password_hash(password)
        new_user = User(username=username, password=password)
        db.session.add(new_user)

        for subject in subjects_interested_in:
            subject = db.session.query(Subject).get(subject)
            if subject is not None:
                subject.students.append(new_user)

        db.session.commit()

        return jsonify({'status': 'success', 'user_id': new_user.id})


@users_module.route('/login/', methods=['POST'])
@users_module.route('/login', methods=['POST'])
def login():
    errors = {}

    username = request.form.get('username')
    if username is None:
        errors['username'] = 'Username not defined.'
    elif not username.strip():
        errors['username'] = 'Please enter your username.'

    password = request.form.get('password')
    if password is None:
        errors['password'] = 'Password not  defined.'
    elif not password.strip():
        errors['password'] = 'Please enter your password.'

    if errors:
        return jsonify({'status': 'error', 'errors': errors})

    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        if check_password_hash(user.password, password):
            return jsonify({'status': 'success', 'user_id': user.id, 'authentication': 'You have been logged in successfully.'})
        else:
            error = {}
            error['main'] = 'Username and Password does not match.'
            return jsonify({'status': 'error', 'errors': error})
    else:
        error = {}
        error['main'] = 'Username and Password does not match.'
        return jsonify({'status': 'error', 'errors': error})


@users_module.route('/<int:user_id>/', methods=['GET'])
@users_module.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(User).get(user_id)
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 102)

    return jsonify({'status': 'success', 'user': user.serialize()})


@users_module.route('/<int:user_id>/chats/', methods=['GET'])
@users_module.route('/<int:user_id>/chats', methods=['GET'])
def get_chats(user_id):
    user = db.session.query(User).get(user_id)
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 103)

    chats_json = []
    for chat in user.chats:
        chats_json.append(chat.serialize())

    if not chats_json:
        return make_error('No chats found with user_id: ' + str(user_id), 104)

    return jsonify({'status': 'success', 'chats': chats_json})


@users_module.route('/<int:user_id>/add_interested_subject/', methods=['POST'])
@users_module.route('/<int:user_id>/add_interested_subject', methods=['POST'])
def add_interested_subject(user_id):
    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name not defined.', 105)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 106)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 107)

    user = db.session.query(User).get(user_id)
    subject.students.append(user)
    db.session.commit()

    return jsonify({'status': 'success'})


@users_module.route('/<int:user_id>/remove_interested_subject/', methods=['POST'])
@users_module.route('/<int:user_id>/remove_interested_subject', methods=['POST'])
def remove_interested_subject(user_id):
    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name not defined.', 108)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 109)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 110)

    user = db.session.query(User).get(user_id)
    subject.students.remove(user)
    db.session.commit()

    return jsonify({'status': 'success'})
