import datetime
from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Question, User, Subject
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


@questions_module.route('/<string:subject_name>/', methods=['GET'])
@questions_module.route('/<string:subject_name>', methods=['GET'])
def get_question_by_subject(subject_name):
    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 302)

    questions = db.session.query(Question).filter_by(subject=subject).all()

    questions_json = []
    for question in questions:
        questions_json.append(question.serialize())

    if not questions_json:
        return make_error('No question found.', 303)

    return jsonify({'status': 'success', 'questions': questions_json})


@questions_module.route('/<int:question_id>/', methods=['GET'])
@questions_module.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return make_error('No question found with question_id: ' + str(question_id), 304)

    return jsonify({'status': 'success', 'questions': question.serialize()})


@questions_module.route('/new/', methods=['POST'])
@questions_module.route('/new', methods=['POST'])
def create_question():
    question = request.form.get('question')
    if question is None:
        return make_error('question is not defined.', 305)
    elif not question.strip():
        return make_error('Question field cannot be empty.', 306)

    title = request.form.get('title')
    if title is None:
        return make_error('title is not defined.', 307)
    elif not title.strip():
        return make_error('Title field cannot be empty.', 308)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 309)
    elif not user_id.strip():
        return make_error('user_id cannot be empty.', 310)

    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 311)

    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name is not defined.', 312)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 313)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + user_id, 314)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 315)

    new_question = Question(question=question, title=title, user=user, subject=subject)

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'status': 'success', 'question_id': new_question.id})


@questions_module.route('/update/<int:question_id>/', methods=['POST'])
@questions_module.route('/update/<int:question_id>', methods=['POST'])
def update_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return make_error('No question was found with id: ' + str(question_id), 316)

    new_question = request.form.get('question')
    if new_question is not None:
        if not new_question.strip():
            return make_error('Question field cannot be empty.', 317)
        else:
            question.question = new_question
    else:
        return make_error('question is not defined.', 318)

    new_title = request.form.get('title')
    if new_title is not None:
        if not new_title.strip():
            return make_error('Title field cannot be empty.', 319)
        else:
            question.title = new_title
    else:
        return make_error('title is not defined.', 320)

    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name is not defined.', 321)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 322)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 323)

    question.subject = subject

    question.updated_on = datetime.datetime.utcnow()

    db.session.commit()

    return jsonify({'status': 'success'})
