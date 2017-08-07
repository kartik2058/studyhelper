from flask import jsonify, Blueprint
from StudyHelper.models import db, Question

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
