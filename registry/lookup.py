__author__ = 'udaymittal'

from flask import Flask, json, request
from repository import get_region_name

app = Flask(__name__)

# static list of topics
topics = ['Food', 'Sports', 'Pub', 'Gas']


@app.route('/topiclist/')
def get_topic_list():
    return json.dumps(topics)


@app.route('/region')
def get_region():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    name = get_region_name(longitude, latitude)
    return json.dumps(name)


if __name__ == '__main__':
    # app.debug = True
    app.run(host="0.0.0.0")

