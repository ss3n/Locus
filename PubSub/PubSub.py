from flask import Flask, request
import KafkaAPI


app = Flask(__name__)


@app.route('/hello')
def hello_world():
    return 'Hello World!'


@app.route('/publish/', methods=['POST'])
def publish():
    topic = request.form['topic']
    message = request.form['ad']
    KafkaAPI.publish(topic, message)


@app.route('/subscribe/', methods=['GET'])
def subscribe():
    topic = request.form['topic']
    subscription = KafkaAPI.subscribe(topic)
    return subscription


if __name__ == '__main__':
    app.run()