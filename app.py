from flask import Flask, jsonify
from flask_cors import CORS
from piazza_api import Piazza



def post_decorate(post):
    content = post["history"][0]["content"] \
        .replace("<p>", "").replace("</p>", "").replace("\n", "").replace("<div>", "")\
        .replace("<md>", "").replace("</md>", "") \
        .replace("</div>", "").replace("<br />", "").replace("&#34;", "\"").replace("&#39;", "\'")
    post_detail = {"subject": post["history"][0]["subject"], "content": content}
    post_answers = post["children"]
    ans_list = []

    for answer in post_answers:
        if "history" in answer:
            ans_content = answer["history"][0]["content"] \
                .replace("<p>", "").replace("</p>", "").replace("\n", "").replace("<div>", "")\
                .replace("<md>","").replace("</md>", "") \
                .replace("</div>", "").replace("<br />", "").replace("&#34;", "\"").replace("&#39;", "\'")
            ans_list.append({
                "type": answer["type"],
                "content": ans_content,
                "vote": len(answer["tag_endorse"])
            })

    return {"id": post["id"], "nr": post["nr"], "time": post["created"], "vote": len(post["tag_good"]), "detail": post_detail,
                                     "answers": ans_list}


def posts_decorate(posts):
    posts_list = []
    for post in posts:
        if post['type'] == "question":
            posts_list.append(post_decorate(post))
    return posts_list


def posts_first_question(posts):
    for post in posts:
        if post["type"] == "question":
            return post_decorate(post)

    return {}


app = Flask(__name__)
CORS(app)


@app.route('/users')
def course_list():
    # Get user course list
    if p:
        class_profile = p.get_user_profile()['all_classes']
        class_list = [{"id": key, "name": value["num"]} for key, value in class_profile.items()]
        return class_list
    else:
        return 'Piazza instance not available'


@app.route('/courses/<cid>/newest_post')
def newest_posts(cid):
    # Get the newest post
    if p:
        course = p.network(cid)
        posts = course.iter_all_posts(limit=10)
        return posts_first_question(posts)
    else:
        return 'Piazza instance not available'


@app.route('/courses/<cid>/all_posts')
def all_posts(cid):
    # Get course post list
    if p:
        course = p.network(cid)
        posts = course.iter_all_posts(sleep=1)
        return jsonify(posts_decorate(posts))
    else:
        return 'Piazza instance not available'


if __name__ == '__main__':
    print("Piazza Authentication------------")
    p = Piazza()
    p.user_login()
    print("Authentication Succeed-----------")
    app.run()
