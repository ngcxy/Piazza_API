from flask import Flask, request, jsonify
from flask_cors import CORS
from auth_manager import AuthManager
from custom_piazza_api.exceptions import AuthenticationError
from beautifulPiazza import BeautifulPiazza

a = AuthManager()

app = Flask(__name__)
CORS(app)


# ------------ test endpoints -------------
@app.route('/test/sessions', methods=['GET'])
def test_sessions():
    a.test_sessions()
    return jsonify(message='See print out'), 200


@app.route('/test/<email>/<cid>/course_posts', methods=['GET'])
def test_course_posts(email, cid):
    bp = BeautifulPiazza(session=a.sessions[email])
    num = bp.get_post_num(cid)
    return jsonify(num), 200

# ------------ test endpoints -------------


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        a.login(email=email, password=password)
        print(f"{email} logged in!")
        return jsonify(message='Login successfully'), 200
    except AuthenticationError:
        return jsonify(message='Invalid credentials'), 401


@app.route('/users/logout', methods=['POST'])
def logout():
    data = request.get_json()
    email = data.get('email')
    try:
        a.logout(email=email)
        print(f"{email} logged out!")
        return jsonify(message='Logout successfully'), 200
    except ValueError:
        return jsonify(message='Invalid credentials'), 401


@app.route('/users/<email>/courses/all')
def all_course(email):
    # Get user course list
    if email in a.sessions:
        bp = BeautifulPiazza(session=a.sessions[email])
        return jsonify(bp.get_user_courses()), 200
    else:
        return jsonify(message='User not found'), 401


@app.route('/users/<email>/courses/<cid>/posts/all')
def all_posts(email, cid):
    # Get course post list
    if email in a.sessions:
        bp = BeautifulPiazza(session=a.sessions[email])
        return jsonify(bp.get_post_all(cid)), 200
    else:
        return jsonify(message='User not found'), 401


@app.route('/users/<email>/courses/<cid>/posts/unread')
def unread_posts(email, cid):
    # Get unread post
    if email in a.sessions:
        bp = BeautifulPiazza(session=a.sessions[email])
        return jsonify(bp.get_post_unread(cid)), 200
    else:
        return jsonify(message='Invalid user'), 401


@app.route('/users/<email>/courses/<cid>/folders/<fname>')
def folder_posts(email, cid, fname):
    if email in a.sessions:
        bp = BeautifulPiazza(session=a.sessions[email])
        posts = bp.get_post_in_folder(cid, fname)
        return jsonify(posts), 200
    else:
        return jsonify(message='Invalid user'), 401


@app.route('/users/<email>/courses/<cid>/posts/<pid>')
def one_post(email, cid, pid):
    if email in a.sessions:
        bp = BeautifulPiazza(session=a.sessions[email])
        post = bp.get_post(cid, pid)
        return jsonify(post), 200
    else:
        return jsonify(message='Invalid user'), 401


@app.route('/users/<email>/courses/<cid>/posts/<pid>', methods=['POST'])
def create_student_reply(email, cid, pid):
    if email in a.sessions:
        data = request.get_json()
        content = data.get('content')
        revision = int(data.get('revision', 0))
        user_type = data.get('user_type', "i")
        bp = BeautifulPiazza(session=a.sessions[email])
        if bp.create_reply(cid, pid, content, revision, user_type) == 0:
            return jsonify(message='Posted!'), 200
        else:
            return jsonify(message='Invalid Role!'), 401
    else:
        return jsonify(message='Invalid user'), 401


if __name__ == '__main__':
    app.run(port=5500)
