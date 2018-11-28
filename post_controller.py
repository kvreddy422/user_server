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
    sub = request.json['subTopic']
    subtopic = SubTopic.find_one({"name": sub, "code": obj['code']})
    obj['subtopic'] = subtopic
    obj['up_votes'] = 0
    obj['down_votes'] = 0
    obj['created_user'] = user
    obj['upvote_users'] = []
    obj['downvote_users'] = []
    return obj

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


# def update_up_vote():
#     note = find_post(request.json['_id'])
#     up_vote_user = Set(note['up_vote_users'])
#     down_vote_user = Set(note['down_vote_users'])

def find_post(id):
    Post = mongo.db.Post
    note = Post.find_one({"_id": ObjectId(id)})
    return note