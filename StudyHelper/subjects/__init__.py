from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Subject
from StudyHelper import make_error

subjects_module = Blueprint('subjects', __name__)


@subjects_module.route('/', methods=['GET'])
@subjects_module.route('', methods=['GET'])
def get_subjects():
    subjects = db.session.query(Subject).all()
    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    if not subjects_json:
        return make_error('No subjects found.', 201)

    return jsonify({'status': 'success', 'subjects': subjects_json})


@subjects_module.route('/<int:subject_id>/', methods=['GET'])
@subjects_module.route('/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = db.session.query(Subject).get(int(subject_id))

    if subject is None:
        return make_error('No subject found.', 202)

    return jsonify({'status': 'success', 'subject': subject.serialize()})


@subjects_module.route('/search/<string:subject_name>/', methods=['GET'])
@subjects_module.route('/search/<string:subject_name>', methods=['GET'])
def search_subjects(subject_name):
    subjects = db.session.query(Subject).filter(Subject.name.like(subject_name+'%')).all()

    if not subjects:
        return make_error('No subjects found', 203)

    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    return jsonify({'status': 'success', 'subjects': subjects_json})


@subjects_module.route('/new/', methods=['POST'])
@subjects_module.route('/new', methods=['POST'])
def create_subject():
    name = request.form.get('name')
    if name is None:
        return make_error('Subject name is not defined.', 204)
    else:
        if not name.strip():
            return make_error('Subject name cannot be empty', 205)

    existing_subject = db.session.query(Subject).filter_by(name=name).first()
    if existing_subject is not None:
        return make_error(name + 'is already present', 206, 'existing_subject_id', existing_subject.id)

    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify({'status': 'success', 'subject_id': subject.id})