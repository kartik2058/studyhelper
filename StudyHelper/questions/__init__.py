from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Question, User
from StudyHelper import make_error

questions_module = Blueprint('questions', __name__)


@questions_module.route('/', methods=['GET'])
@questions_module.route('', methods=['GET'])
def get_questions():
    questions = db.session.query(Question).all()

    questions_json = []
    for question in questions:
        questions_json.append(question.serialize())

    if not questions_json:
        return make_error('No questions found', 301)

    return jsonify({'status': 'success', 'questions': questions_json})


@questions_module.route('/<int:question_id>/', methods=['GET'])
@questions_module.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return make_error('No question found.', 302)

    return jsonify({'status': 'success', 'questions': question.serialize()})


@questions_module.route('/new/', methods=['POST'])
@questions_module.route('/new', methods=['POST'])
def create_question():
    question = request.form.get('question')
    if question is None:
        return make_error('question is not defined.', 303)
    elif not question.strip():
        return make_error('question cannot be empty.', 304)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 305)
    elif not user_id.strip():
        return make_error('user_id cannot be empty.', 306)

    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 307)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 308)

    new_question = Question(question=question, user=user)

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'status': 'success', 'question_id': new_question.id})