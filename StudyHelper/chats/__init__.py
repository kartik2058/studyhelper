from flask import jsonify, request, Blueprint
from StudyHelper.models import db, Chat, User, Subject
from StudyHelper import make_error

chats_module = Blueprint('chats', __name__)


@chats_module.route('/subjects/<string:subject_names>/', methods=['GET'])
@chats_module.route('/subjects/<string:subject_names>', methods=['GET'])
def get_chats(subject_names):
    subject_names = subject_names.split(',')

    subjects = []
    for subject_name in subject_names:
        subjects.append(db.session.query(Subject).filter_by(name=subject_name).first())

    chats = db.session.query(Chat).all()

    chats_json = []
    for chat in chats:
        is_addable = False
        for subject in subjects:
            if chat.subject == subject:
                is_addable = True
        if is_addable:
            chats_json.append(chat.serialize())

    if not chats_json:
        return make_error('No chats found.', 601)

    return jsonify({'status': 'success', 'chats': chats_json})


@chats_module.route('/users/<int:user_id>/', methods=['GET'])
@chats_module.route('/users/<int:user_id>', methods=['GET'])
def get_chats_by_user(user_id):
    user = db.session.query(User).get(user_id)
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 602)

    chats = db.session.query(Chat).all()

    chats_json = []
    for chat in chats:
        for chat_user in chat.users:
            if chat_user == user:
                chats_json.append(chat.serialize())

    if not chats_json:
        return make_error('No chat found.', 603)

    return jsonify({'status': 'success', 'chats': chats_json})


@chats_module.route('/<int:chat_id>/', methods=['GET'])
@chats_module.route('/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    chat = db.session.query(Chat).get(chat_id)

    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 604)

    return jsonify({'status': 'success', 'chat': chat.serialize()})


@chats_module.route('/new/', methods=['POST'])
@chats_module.route('/new', methods=['POST'])
def create_chat():
    question = request.form.get('question')
    if question is None:
        return make_error('question is not defined.', 605)
    elif not question.strip():
        return make_error('Questions cannot be empty', 606)

    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name is not defined.', 607)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 608)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 609)

    chat = Chat(question=question, subject=subject)
    db.session.add(chat)
    db.session.commit()

    return jsonify({'status': 'success', 'chat_id': chat.id})


@chats_module.route('/<int:chat_id>/add_member/<int:user_id>/', methods=['POST'])
@chats_module.route('/<int:chat_id>/add_member/<int:user_id>', methods=['POST'])
def add_member(chat_id, user_id):
    chat = db.session.query(Chat).get(chat_id)
    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 610)

    user = db.session.query(User).get(user_id)
    if user is None:
        return make_error('No user found with id: ' + str(user_id), 611)

    chat.users.append(user)
    db.session.commit()

    return jsonify({'status': 'success'})


@chats_module.route('/<int:chat_id>/delete/', methods=['POST'])
@chats_module.route('/<int:chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    chat = db.session.query(Chat).get(chat_id)
    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 612)

    db.session.delete(chat)
    db.session.commit()
    return jsonify({'status': 'success'})