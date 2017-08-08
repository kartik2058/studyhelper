import datetime
from flask import request, jsonify, Blueprint
from StudyHelper.models import db, Comment, Answer, User
from StudyHelper import make_error

comments_module = Blueprint('comments', __name__)


@comments_module.route('/', methods=['GET'])
@comments_module.route('', methods=['GET'])
def get_comments(answer_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 501)

    comments = db.session.query(Comment).filter_by(answer=answer).all()

    comments_json = []
    for comment in comments:
        comments_json.append(comment.serialize())

    if not comments_json:
        return make_error('No comments found.', 502)

    return jsonify({'status': 'success', 'comments': comments_json})


@comments_module.route('/<int:comment_id>/', methods=['GET'])
@comments_module.route('/<int:comment_id>', methods=['GET'])
def get_comment(answer_id, comment_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 503)

    comment = None
    for looping_comment in answer.comments:
        if looping_comment.id == comment_id:
            comment = looping_comment

    if comment is None:
        return make_error('No comment found with comment_id: ' + str(comment_id) + ' and answer_id: ' + str(answer_id), 504)

    return jsonify({'status': 'success', 'comment': comment.serialize()})


@comments_module.route('/new/', methods=['POSt'])
@comments_module.route('/new', methods=['POSt'])
def create_comment(answer_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 505)

    comment = request.form.get('comment')
    if comment is None:
        return make_error('comment is not defined.', 506)
    if not comment.strip():
        return make_error('Comment field cannot be empty.', 507)

    user_id = request.form.get('user_id')
    if user_id is None:
        return make_error('user_id is not defined.', 508)
    if not user_id.strip():
        return make_error('user_id cannot be empty.', 509)
    try:
        int(user_id)
    except:
        return make_error('user_id is invalid.', 510)

    user = db.session.query(User).get(int(user_id))
    if user is None:
        return make_error('No user found with user_id: ' + user_id, 511)

    new_comment = Comment(comment=comment, answer=answer, user=user)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'status': 'success', 'comment_id': new_comment.id})


@comments_module.route('/<int:comment_id>/update/', methods=['POST'])
@comments_module.route('/<int:comment_id>/update', methods=['POST'])
def update_comment(answer_id, comment_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 512)

    comment = None
    for looping_comment in answer.comments:
        if looping_comment.id == comment_id:
            comment = looping_comment

    if comment is None:
        return make_error('No comment found with id: ' + str(comment_id), 513)

    new_comment = request.form.get('comment')
    if new_comment is None:
        return make_error('comment is not defined.', 514)
    if not new_comment.strip():
        return make_error('Comment field cannot be empty.', 515)

    comment.comment = new_comment
    comment.updated_on = datetime.datetime.utcnow()

    db.session.commit()

    return jsonify({'status': 'success'})


@comments_module.route('/<int:comment_id>/delete/', methods=['POST'])
@comments_module.route('/<int:comment_id>/delete', methods=['POST'])
def delete_comment(answer_id, comment_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is None:
        return make_error('No answer found with id: ' + str(answer_id), 516)

    comment = None
    for looping_comment in answer.comments:
        if looping_comment.id == comment_id:
            comment = looping_comment

    if comment is None:
        return make_error('No comment found with id: ' + str(comment_id), 517)

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'status': 'success'})