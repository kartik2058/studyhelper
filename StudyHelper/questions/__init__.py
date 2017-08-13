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


@questions_module.route('/subject/<string:subject_name>/', methods=['GET'])
@questions_module.route('/subject/<string:subject_name>', methods=['GET'])
def get_questions_by_subject(subject_name):
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


@questions_module.route('/subjects/<string:subject_names>/', methods=['GET'])
@questions_module.route('/subjects/<string:subject_names>', methods=['GET'])
def get_questions_by_subjects(subject_names):
    if not subject_names.strip():
        return make_error('subject_name cannot be empty.', 304)

    subject_names = subject_names.split(',')
    subjects = []
    for subject in subject_names:
        subjects.append(db.session.query(Subject).filter_by(name=subject).first())

    questions = db.session.query(Question).order_by(db.desc(Question.posted_on)).all()

    questions_json = []
    for question in questions:
        is_addable = False
        for subject in subjects:
            if question.subject == subject:
                is_addable = True
        if is_addable:
            questions_json.append(question.serialize())

    if not questions_json:
        return make_error('No questions found.', 305)

    return jsonify({'status': 'success', 'questions': questions_json})


@questions_module.route('/<int:question_id>/', methods=['GET'])
@questions_module.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return make_error('No question found with question_id: ' + str(question_id), 306)

    return jsonify({'status': 'success', 'questions': question.serialize()})


@questions_module.route('/new/', methods=['POST'])
@questions_module.route('/new', methods=['POST'])
def create_question():
    question = request.form.get('question')
    if question is None:
        return make_error('question is not defined.', 307)
    elif not question.strip():
        return make_error('Question field cannot be empty.', 308)

    title = request.form.get('title')
    if title is None:
        return make_error('title is not defined.', 309)
    elif not title.strip():
        return make_error('Title field cannot be empty.', 310)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 311)
    elif not user_id.strip():
        return make_error('user_id cannot be empty.', 312)

    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 313)

    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name is not defined.', 314)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 315)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + user_id, 316)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 317)

    new_question = Question(question=question, title=title, user=user, subject=subject)

    db.session.add(new_question)
    db.session.commit()

    return jsonify({'status': 'success', 'question_id': new_question.id})


@questions_module.route('/update/<int:question_id>/', methods=['POST'])
@questions_module.route('/update/<int:question_id>', methods=['POST'])
def update_question(question_id):
    question = db.session.query(Question).get(question_id)

    if question is None:
        return make_error('No question was found with id: ' + str(question_id), 318)

    new_question = request.form.get('question')
    if new_question is not None:
        if not new_question.strip():
            return make_error('Question field cannot be empty.', 319)
        else:
            question.question = new_question
    else:
        return make_error('question is not defined.', 320)

    new_title = request.form.get('title')
    if new_title is not None:
        if not new_title.strip():
            return make_error('Title field cannot be empty.', 321)
        else:
            question.title = new_title
    else:
        return make_error('title is not defined.', 322)

    subject_name = request.form.get('subject_name')
    if subject_name is None:
        return make_error('subject_name is not defined.', 323)
    elif not subject_name.strip():
        return make_error('subject_name cannot be empty.', 324)

    subject = db.session.query(Subject).filter_by(name=subject_name).first()
    if subject is None:
        return make_error('No subject found with subject_name: ' + subject_name, 325)

    question.subject = subject

    question.updated_on = datetime.datetime.utcnow()

    db.session.commit()

    return jsonify({'status': 'success'})
