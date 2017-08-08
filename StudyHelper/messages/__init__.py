from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Message, Chat, User
from StudyHelper import make_error

messages_module = Blueprint('messages', __name__)


@messages_module.route('/', methods=['GET'])
@messages_module.route('', methods=['GET'])
def get_messages(chat_id):
    chat = db.session.query(Chat).get(chat_id)
    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 701)

    messages = db.session.query(Message).filter_by(chat=chat).all()

    messages_json = []
    for message in messages:
        messages_json.append(message.serialize())

    if not messages_json:
        return make_error('No messages found.', 702)

    return jsonify({'status': 'success', 'messages': messages_json})


@messages_module.route('/<int:message_id>/', methods=['GET'])
@messages_module.route('/<int:message_id>', methods=['GET'])
def get_message(chat_id, message_id):
    chat = db.session.query(Chat).get(chat_id)
    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 703)

    found_message = None
    for message in chat.messages:
        if message.id == message_id:
            found_message = message

    if found_message is None:
        return make_error('No message found with chat_id: ' + str(chat_id) + ' and message_id: ' + str(message_id), 704)

    return jsonify({'status': 'success', 'message': found_message.serialize()})


@messages_module.route('/new/', methods=['POST'])
@messages_module.route('/new', methods=['POST'])
def create_message(chat_id):
    chat = db.session.query(Chat).get(chat_id)
    if chat is None:
        return make_error('No chat found with id: ' + str(chat_id), 705)

    message = request.form.get('message')
    if message is None:
        return make_error('message is not defined.', 706)
    elif not message.strip():
        return make_error('Message cannot be empty.', 707)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 708)
    elif not user_id.strip():
        return make_error('user_id cannot be empty.', 709)
    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 710)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 711)

    new_message = Message(message=message, chat=chat, user=user)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'status': 'success', 'message_id': new_message.id})