from flask import Flask, request, render_template
import json
import KafkaAPI


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('subscribe-ad.html')


@app.route('/publish/', methods=['POST'])
def publish():
    ad = json.loads(request.get_json())
    topics = ad['topiclist']
    message = ad['content']

    app.logger.debug(topics)
    app.logger.debug(message)

    KafkaAPI.publish(topics, message)
    return 'PUBLISHED!'


@app.route('/poll/', methods=['POST'])
def poll():
    topics = json.loads(request.get_json())
    msgs = dict()
    for topic, offset in topics.items():
        msgs[topic] = KafkaAPI.poll(topic, offset)
    return topics


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
