import requests
import time
import warnings
from custom_piazza_api.piazza import Piazza
from custom_piazza_api.exceptions import RequestError
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

from custom_piazza_api.network import UnreadFilter, FolderFilter

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")


class BeautifulPiazza:
    def __init__(self, session=None):
        self.session = session if session else requests.Session()
        self.p = Piazza(session=self.session)

    def get_user_courses(self):
        course_profile = self.p.get_user_profile()['all_classes']
        return [{"id": key, "name": value["num"]} for key, value in course_profile.items()]

    def get_post(self, cid, pid):
        course = self.p.network(cid)
        post = course.get_post(pid)
        return post

    def get_post_all(self, cid):
        post_num = self.get_post_num(cid)
        course = self.p.network(cid)
        post_list = []
        folder_list = set()
        print(f"Total post number: {post_num}")
        for i in range(2, post_num+1):
            print(f"Getting post {i} ......", end="")
            try:
                post = course.get_post(i)
                if post["status"] == "deleted":
                    print("Post doesn't exist!")
                    continue
                post_list.append(self.common_deco(post))
                print("Succeed!")
            except RequestError:
                print("Post doesn't exist!")
                continue
            time.sleep(1)
        return post_list

    def get_post_unread(self, cid):
        print("Getting unread posts ......")
        course = self.p.network(cid)
        unread_filter = UnreadFilter()
        feeds = course.get_filtered_feed(feed_filter=unread_filter)
        return self.feed_to_post(course, feeds)

    def get_post_in_folder(self, cid, fname):
        print(f"Getting post in folder {fname} ......")
        course = self.p.network(cid)
        folder_filter = FolderFilter(folder_name=fname)
        feeds = course.get_filtered_feed(feed_filter=folder_filter)
        return self.feed_to_post(course, feeds)

    def create_reply(self, cid, pid, content, revision=0, post_type="i"):
        course = self.p.network(cid)
        post = course.get_post(pid)
        try:
            if post_type == "s":
                course.create_student_answer(post, content, revision)
            if post_type == "i":
                course.create_instructor_answer(post, content, revision)
        except RequestError:
            return 1
        print(f"Posting... {content}")
        print("Posted!")
        return 0

    ###################
    # Private Methods #
    ###################
    def get_post_num(self, cid):
        course = self.p.network(cid)
        max_num = 0
        posts = course.iter_all_posts(limit=10)
        for post in posts:
            max_num = max(max_num, post["nr"])
        return max_num

    def single_deco(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        deco_content = soup.get_text(strip=True)
        return deco_content
    
    def question_deco(self, post):
        content = self.single_deco(post["history"][0]["content"])
        post_detail = {"subject": post["history"][0]["subject"], "content": content}
        post_answers = post["children"]
        ans_list = []
        for answer in post_answers:
            if "history" in answer:
                ans_content = self.single_deco(answer["history"][0]["content"])
                ans_list.append({
                    "type": answer["type"],
                    "content": ans_content,
                    "vote": len(answer["tag_endorse"])
                })

        return {
            "id": post["id"],
            "id_c": post["nr"],
            "type": "question",
            "folders": post["folders"],
            "time": post["created"],
            "vote": len(post["tag_good"]),
            "detail": post_detail,
            "answers": ans_list
        }

    def note_deco(self, post):
        content = self.single_deco(post["history"][0]["content"])
        post_detail = {"subject": post["history"][0]["subject"], "content": content}

        return {
            "id": post["id"],
            "id_c": post["nr"],
            "type": "note",
            "folders": post["folders"],
            "time": post["created"],
            "vote": len(post["tag_good"]),
            "detail": post_detail,
        }

    def common_deco(self, post):
        if post["type"] == "question":
            return self.question_deco(post)
        if post["type"] == "note":
            return self.note_deco(post)

    def feed_to_post(self, course, feeds):
        posts = []
        for post in feeds["feed"]:
            post_id = post["nr"]
            print(f"Getting post {post_id} ......", end="")
            try:
                p = course.get_post(post_id)
                posts.append(self.common_deco(p))
                print("Succeed!")
            except RequestError:
                print("Failed!")
                continue
        return posts
