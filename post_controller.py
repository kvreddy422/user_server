from flask import Flask, request
from flask import Response
from flask import jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson import json_util, ObjectId
import json
import datetime
import bcrypt
from bson.objectid import ObjectId
import study_global

app = Flask(__name__)
app.config["MONGO_URI"] = study_global.URI
mongo = PyMongo(app)


def add_post(request, user):
    Post = mongo.db.Post
    post_object = create_post_obj(request, user)
    new_post = Post.insert(post_object)
    return Response(dumps(new_post), status=200)


def create_post_obj(request, user):
    SubTopic = mongo.db.SubTopic
    obj= {}
    obj['title'] = request.json['title']
    obj['tags'] = request.json['tags']
    obj['content'] = request.json['content']
    obj['code'] = request.json['code']
    if 'group' in request.json:
        obj['group'] = request.json['group']
    sub = request.json['subTopic']
    subtopic = SubTopic.find_one({"name": sub, "code": obj['code']})
    obj['subtopic'] = subtopic
    obj['up_votes'] = 0
    obj['down_votes'] = 0
    obj['pinned'] = 0
    obj['pinned_users'] = []
    obj['created_user'] = user
    obj['upvote_users'] = []
    obj['downvote_users'] = []
    obj['created_time'] = str(datetime.datetime.now())
    return obj

def create_comment(request, user):
    note = find_post(request.json['_id'])
    comments = {}
    if 'comments' not in note:
        comment_array = []
        comments['id'] = 1
    else:
        comment_array = note['comments']
        comments['id'] = note['comments'][len(note['comments'])-1]['id'] + 1
    comments['comment'] = request.json['comment']
    comments['user'] = user['user_name']
    comments['created_time'] = str(datetime.datetime.now())
    comment_array.append(comments)
    note['comments'] = comment_array
    Post = mongo.db.Post
    Post.update_one({'_id': note['_id']}, {"$set": note}, upsert=False)
    return note

def upvote_post(request, user):
    note = find_post(request.json['_id'])
    note['up_votes'] = note['up_votes'] + 1
    if (len(note['upvote_users']) == 0):
        userList = []
        userList.append(user['user_name'])
        note['upvote_users'] = userList
    else:
        note['upvote_users'] = note['upvote_users'].append(user['user_name'])
    if (set(note['downvote_users']).__contains__(user['user_name'])):
        note['down_votes'] = note['down_votes'] - 1
        down_vote_users = set(note['downvote_users'])
        note['downvote_users'] = down_vote_users.remove(user['user_name'])
    Post = mongo.db.Post
    Post.update_one({'_id': note['_id']}, {"$set": note}, upsert=False)
    return note

def downvote_post(request, user):
    note = find_post(request.json['_id'])
    note['down_votes'] = note['down_votes'] + 1
    if (len(note['downvote_users']) == 0):
        userList = []
        userList.append(user['user_name'])
        note['downvote_users'] = userList
    else:
        note['downvote_users'] = note['downvote_users'].append(user['user_name'])
    if(note['upvote_users']  != None):
        if (set(note['upvote_users']).__contains__(user['user_name'])):
            note['up_votes'] = note['up_votes'] - 1
            up_vote_users = set(note['upvote_users'])
            note['upvote_users'] = up_vote_users.remove(user['user_name'])
    Post = mongo.db.Post
    Post.update_one({'_id': note['_id']}, {"$set": note}, upsert=False)
    return note

def pin_post(request, user):
    note = find_post(request.json['_id'])
    note['pinned'] = note['pinned'] + 1
    if (len(note['pinned_users']) == 0):
        userList = []
        userList.append(user['user_name'])
        note['pinned_users'] = userList
    else:
        note['pinned_users'] = note['pinned_users'].append(user['user_name'])
    Post = mongo.db.Post
    Post.update_one({'_id': note['_id']}, {"$set": note}, upsert=False)
    return note

def unpin_post(request, user):
    note = find_post(request.json['_id'])
    note['pinned'] = note['pinned'] - 1
    if (len(note['pinned_users']) == 0):
        return note
    else:
        users = set(note['pinned_users'])
        note['pinned_users'] = users.remove(user['user_name'])
    Post = mongo.db.Post
    Post.update_one({'_id': note['_id']}, {"$set": note}, upsert=False)
    return note


def get_posts(request, user):
    Post = mongo.db.Post
    notes = Post.find()
    response_final = []
    # if 'group'  in notes:
    #     notes =Post.find({"group": str(ObjectId(request.json['group']))})
    # else:
    #     notes = Post.find({"group": {"$exists": False}})
    # response_final = []
    group = 0
    query = []
    if len(request.query_string) != 0:
        query = request.query_string.decode().split('=')
        group = 1

    for post in notes:
        response = {}
        if group == 1:
            if 'group' in post and post['group'] == query[1]:
                response['group'] = post['group']
            else:
                continue

        if group == 0:
            if 'group' in post:
                continue
        response['id'] = str(ObjectId(post['_id']))
        response['upvotes'] = post['up_votes']
        response['downvotes'] = post['down_votes']
        if 'comments' in post:
            response['comments'] = post['comments']
        if 'pinned' in post:
            response['pinned'] = post['pinned']
            response['pinned_users'] = post['pinned_users']
        response['tags'] = post['tags']
        response['title'] = post['title']
        response['content'] = post['content']
        response['title'] = post['title']
        response['code'] = post['code']
        response['subtopic'] = {}
        response['subtopic']['code'] = post['subtopic']['code']
        response['subtopic']['name'] = post['subtopic']['name']
        response['subtopic']['description'] = post['subtopic']['Description']
        response['subtopic']['course'] = {}
        response['subtopic']['course']['name'] = post['subtopic']['course']['name']
        response['subtopic']['course']['Description'] = post['subtopic']['course']['Description']
        response['subtopic']['course']['code'] = post['subtopic']['course']['code']
        response['created_time'] = str(post['created_time'])
        response['created_user'] = post['created_user']['user_name']
        response['user_upvoted'] = 0
        response['user_downvoted'] = 0
        upvoted_users = post['upvote_users']
        if upvoted_users != None:
            for userUpvoted in upvoted_users:
                if userUpvoted == user:
                    response['user_upvoted'] = 1

        downvote_users = post['downvote_users']
        if downvote_users != None:
            for userDownvoted in downvote_users:
                if userDownvoted == user:
                    response['user_downvoted'] = 1
        response_final.append(response)
    return response_final

def find_post(id):
    Post = mongo.db.Post
    note = Post.find_one({"_id": ObjectId(id)})
    return note