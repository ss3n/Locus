__author__ = 'udaymittal'

from flask import Flask, json, abort, request
app = Flask(__name__)

#static list of topics
topics = ['FOOD', 'SPORTS', 'PUB', 'GAS']


@app.route('/topiclist/')
def getTopicList():
    return json.dumps(topics)

@app.route('/region/')
def getRegion():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    app.logger.debug('Latitude: ' + latitude + ", Longitude: " + longitude)
    abort(501)

if __name__ == '__main__':
    app.debug = True
    app.run()