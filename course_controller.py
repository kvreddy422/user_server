from flask import Flask, request
from flask import Response
from flask import jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
import study_global
from bson import json_util, ObjectId
import json
import datetime
import bcrypt
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = study_global.URI
mongo = PyMongo(app)


def create_sub_topics():
    Course = mongo.db.Course
    SubTopic = mongo.db.SubTopic
    subtopics = request.json

    for topic in subtopics:
        course = Course.find_one({'code': topic['code']})
        topic['course'] = course
        topic = SubTopic.insert(topic)
    return Response(dumps({'status': True, 'data': subtopics}), status=200)


def get_course():
    course = mongo.db.Course.find()
    return Response(dumps(course), status=200)


def get_sub_topic(request):
    query = request.query_string.split("=")
    subtopics = mongo.db.SubTopic.find({ 'code': query[1]})
    return Response(dumps(subtopics), status=200)

