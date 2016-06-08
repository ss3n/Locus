from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from time import sleep
import thread
import json
import KafkaAPI


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

sidlist = []


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/publish/', methods=['POST'])
def publish():
    ad = json.loads(request.get_json())
    topics = ad['topiclist']
    message = ad['content']

    app.logger.debug(topics)
    app.logger.debug(message)

    KafkaAPI.publish(topics, message)
    return 'PUBLISHED!'


@socketio.on('connect')
def handle_connect():
    """
    New connection handler that adds a client to the room list
    :return:
    """
    app.logger.debug('Got a client in room: ' + str(request.sid))
    sidlist.append(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    """
    Disconnect handler that removes the client from the room list
    :return:
    """
    app.logger.debug('Removing the room: ' + str(request.sid))
    sidlist.remove(request.sid)


@app.route('/subscribe/', methods=['POST'])
def subscribe():
    interests = json.loads(request.get_json())['interestlist']
    subscription = KafkaAPI.subscribe(interests)
    if len(sidlist) > 0:
        for msg in subscription:
            app.logger.debug(msg.value)
            app.logger.debug(sidlist[0])
            socketio.emit('server-message', msg.value, room=sidlist[0])
            sleep(5)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
