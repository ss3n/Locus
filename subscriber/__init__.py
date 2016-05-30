from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from time import sleep
import requests
import thread
import json

__author__ = 'udaymittal'


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# All clients are assigned a room when they connect, named with the
# session ID of the connection, which can be obtained from request.sid
# Therefore to address a message to a single client, the session ID of the client
# can be used. (request.sid)

sidlist = []
lookupaddr = 'http://0.0.0.0:5000'

@app.route('/subscribe', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
        r = requests.get(lookupaddr+'/region?lat='+str(latitude)+'&lon='+str(longitude))
        publishregion = r.content
        app.logger.debug("Region of publisher: " + str(publishregion))

        # request for list of available topics
        r = requests.get(lookupaddr+'/topiclist')
        topiclist = json.loads(r.content)

        return render_template('subscribe-ad.html', topiclist=topiclist)
    else:
        selectedtopics = request.form.getlist('adcat')

        return "published"



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


@socketio.on('client-message')
def handle_client_message(msg):
    """
    Custom event name example
    :param msg:
    :return:
    """
    # emit message on server-message channel and set a callback for handling delivery
    emit('server-message', ('lele', 'theeke'), callback=ack)
    app.logger.debug('Client message received: ' + msg)
    # return acknowledgement: can be processed as args i client callback
    return 'got it', 'carry on'


def ack():
    """
    Callback for acknowledging whether
    client received the message or not
    :return:
    """
    print "ack"


def messenger():
    """
    Simple stupid test
    :return:
    """
    for i in range(0,100):
        if len(sidlist) > 0:
            idx = i % len(sidlist)
            app.logger.info('Sending message to client in room: ' + str(sidlist[idx]))
            socketio.emit('server-message', {'data': 'Message sent at time: ' + str(i)}, room=sidlist[idx])
        app.logger.info('Messenger in iteration: ' + str(i))
        sleep(5)


if __name__=='__main__':
    app.debug=True
    #thread.start_new_thread(messenger, ())

    socketio.run(app, host="0.0.0.0", port=5200)
