import datetime
from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Answer, Question, User
from StudyHelper import make_error

answers_module = Blueprint('answers', __name__)


@answers_module.route('/', methods=['GET'])
@answers_module.route('', methods=['GET'])
def get_answers(question_id):
    question = db.session.query(Question).get(question_id)
    if question is None:
        return make_error('No question found with id: ' + str(question_id), 401)

    answers = db.session.query(Answer).filter_by(question=question).all()

    answers_json = []
    for answer in answers:
        answers_json.append(answer.serialize())

    if not answers:
        return make_error('No answers found.', 402)

    return jsonify({'status': 'success', 'answers': answers_json})


@answers_module.route('/<int:answer_id>/', methods=['GET'])
@answers_module.route('/<int:answer_id>', methods=['GET'])
def get_answer(question_id, answer_id):
    question = db.session.query(Question).get(question_id)
    if question is None:
        return make_error('No question found with id: ' + str(question_id), 403)

    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 404)

    return jsonify({'status': 'success', 'answer': answer.serialize()})


@answers_module.route('/new/', methods=['POST'])
@answers_module.route('/new', methods=['POST'])
def create_answer(question_id):
    question = db.session.query(Question).get(question_id)
    if question is None:
        return make_error('No question found with id: ' + str(question_id), 405)

    answer = request.form.get('answer')
    if answer is None:
        return make_error('answer is not defined.', 406)
    if not answer.strip():
        return make_error('Answer cannot be empty.', 407)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 408)
    if not user_id.strip():
        return make_error('user_id cannot be empty.', 409)

    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 410)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + str(user_id), 411)

    new_answer = Answer(answer=answer, question=question, user=user)
    db.session.add(new_answer)
    db.session.commit()

    return jsonify({'status': 'success', 'answer_id': new_answer.id})


@answers_module.route('/<int:answer_id>/update/', methods=['POST'])
@answers_module.route('/<int:answer_id>/update', methods=['POST'])
def update_answer(question_id, answer_id):
    question = db.session.query(Question).get(question_id)
    if question is None:
        return make_error('No question found with id: ' + str(question_id), 412)

    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 413)

    new_answer = request.form.get('answer')
    if new_answer is None:
        return make_error('answer is not defined.', 414)
    if not new_answer.strip():
        return make_error('Answer cannot be empty.', 415)

    answer.answer = new_answer
    answer.updated_on = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({'status': 'success'})
