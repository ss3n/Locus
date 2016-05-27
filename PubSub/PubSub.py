from flask import Flask, request
import json
import KafkaAPI


app = Flask(__name__)


@app.route('/hello')
def hello_world():
    return 'Hello World!'


@app.route('/publish/', methods=['GET', 'POST'])
def publish():
    ad = json.loads(request.get_json())
    topics = ad['topiclist']
    message = ad['content']

    app.logger.debug(topics)
    app.logger.debug(message)

    KafkaAPI.publish(topics, message)
    return 'PUBLISHED!'


# @app.route('/subscribe/', methods=['GET'])
# def subscribe():
#     topic = request.form['topic']
#     subscription = KafkaAPI.subscribe(topic)
#     return subscription


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
