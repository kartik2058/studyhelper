from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Question, User

questions_module = Blueprint('questions', __name__)

@questions_module.route('/', methods=['GET'])
@questions_module.route('', methods=['GET'])
def get_questions():
    questions = db.session.query(Question).all()

    questions_json = []
    for question in questions:
        questions_json.append(question.serialize())

    if not questions_json:
        return jsonify({'status': 'error', 'error': 'No questions found.'})

    return jsonify({'status': 'success', 'questions': questions_json})


@questions_module.route('/<int:question_id>/', methods=['GET'])
@questions_module.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return jsonify({'status': 'error', 'error': 'No question found.'})

    return jsonify({'status': 'success', 'questions': question.serialize()})

@questions_module.route('/new/', methods=['POST'])
@questions_module.route('/new', methods=['POST'])
def create_question():
    question = request.form.get('question')
    if question is None:
        return jsonify({'status': 'error', 'error': 'Question not defined.'})

    user_id = request.form.get('user_id')
    if user_id is None:
        return jsonify({'status': 'error', 'error': 'user_id not defined.'})

    user = db.session.query(User).get(user_id)
    if user is None:
        return jsonify({'status': 'error', 'error': 'No user found with user_id: ' + str(user_id)})

    new_question = Question(question=question, user=user)

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'status': 'success', 'question_id': new_question.id})