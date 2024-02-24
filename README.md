## Connect to remote server

### Root Url

    http://lax.nonev.win:5500/

### Endpoints

    
- ### **POST** /users/login

User login

*Request body (in JSON format, raw):*

```
{
    "email":    String,
    "password": String
}
```


- ### **GET** /users/<email>/courses/all
    
Get all course IDs of the user

*Return: a list of courses:* 

```
{
    "id":   String,
    "name": String
}
```


- ### **GET** /users/<email>/courses/<cid>/posts/all

Get all posts of the course (wait about 1 min/50 posts)

*Return: a list of posts:*

If "type"=="question"

```
{
  "answers":[
    {
        "content": String,
        "type": {"i_answer", "s_answer"},
        "vote": Int
    }, 
    {answer2...}, 
    {answer3...},
    ...
  ],
  "detail": {
    "content": String,
    "subject": String
  },
  "folders": [
    "folder_name_1", "folder_name_2", ...
  ],
  "id": String,
  "id_c": Int,
  "time": String,
  "type": {"question", "note"},
  "vote": Int
}
```

If "type"=="note"

```
{
  "detail": {
    "content": String,
    "subject": String
  },
  "folders": [
    "folder_name_1", "folder_name_2", ...
  ],
  "id": String,
  "id_c": Int,
  "time": String,
  "type": {"question", "note"},
  "vote": Int
}
```

*Note: "id" is unique for each post, while "id_c" is the sequential number for the post in particular course.*
*We use "id_c" as the "pid" for that post in most cases.*


- ### **GET** /users/<email>/courses/<cid>/posts/unread

Get all unread posts for the course.

*Return: a list of posts (see above)*


- ### **GET** /users/<email>/courses/<cid>/folders/<fname>

Get all posts in a folder named "fname".

*Return: a list of posts (see above)*


- ### **GET** /users/<email>/courses/<cid>/posts/<pid>

Get the post with a specific pid for the course.

*Return: an object of one post (see above)*

- ### **POST** /users/<email>/courses/<cid>/posts/<pid>

Post a reply as "student answer" to one post.

*Request body (in JSON format, raw):*

```
{
    "content":  String  # the content of your answer
    "revision": String  # enter "0" if create for the first time; add by 1 for each revision
}
```

*Note: For one post, if an answer with revision="n" is already posted, the answer content can be overwritten only when you post a new answer with revision="n+1".*


## How to run locally

1. Install dependencies: `pip install piazza-api flask flask-cors`

2. Start the server: `python app.py`

3. Enter the Piazza email & password in the console

4. For "all post", please allow 4-5 min for loading if the course has a large number of posts

