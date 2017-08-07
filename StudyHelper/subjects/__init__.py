from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Subject

subjects_module = Blueprint('subjects', __name__)


@subjects_module.route('/', methods=['GET'])
def get_subjects():
    subjects = db.session.query(Subject).all()
    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    if not subjects_json:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    return jsonify({'status': 'success', 'subjects': subjects_json})


@subjects_module.route('/<int:subject_id>/', methods=['GET'])
def get_subject(subject_id):
    subject = db.session.query(Subject).get(int(subject_id))

    if subject is None:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    return jsonify({'status': 'success', 'subject': subject.serialize()})


@subjects_module.route('/search/<string:subject_name>/', methods=['GET'])
def search_subjects(subject_name):
    subjects = db.session.query(Subject).filter(Subject.name.like(subject_name+'%')).all()

    if not subjects:
        return jsonify({'status': 'error', 'error': 'No subject found.'})

    subjects_json = []
    for subject in subjects:
        subjects_json.append(subject.serialize())

    return jsonify({'status': 'success', 'subjects': subjects_json})


@subjects_module.route('/new/', methods=['POST'])
def create_subject():
    name = request.form.get('name')
    if name is None:
        return jsonify({'status': 'error', 'error': 'Subject name not defined.'})
    else:
        if not name.strip():
            return jsonify({'status': 'error', 'error': 'Subject name cannot be empty.'})

    existing_subject = db.session.query(Subject).filter_by(name=name).first()
    if existing_subject is not None:
        return jsonify({'status': 'error', 'error': name + ' is already present.',
                        'existing_subject_id': existing_subject.id})

    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify({'status': 'success', 'subject_id': subject.id})