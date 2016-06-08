from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from time import sleep
import requests
from threading import Thread, Lock
import json

__author__ = 'udaymittal'


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# All clients are assigned a room when they connect, named with the
# session ID of the connection, which can be obtained from request.sid
# Therefore to address a message to a single client, the session ID of the client
# can be used. (request.sid)

# client dictionary has the following structure:
#   key: sid
#       key: interest
#           key: region value: [status, offset]
#           key: region value: [status, offset]
#       key: interest
#           ...
#       ...
#   ...

lock = Lock()
client_dict = dict()
lookupaddr = 'http://0.0.0.0:5000'


def collect_topics():
    topic_dict = dict()
    for sid in client_dict.keys():
        for interest in client_dict[sid].keys():
            for region in client_dict[sid][interest].keys():
                if client_dict[sid][interest][region][0]:
                    topic = interest + '*' + region
                    try:
                        if client_dict[sid][interest][region][1] < topic_dict[topic]:
                            topic_dict[topic] = client_dict[sid][interest][region][1]
                    except KeyError:
                        topic_dict[topic] = client_dict[sid][interest][region][1]
    return topic_dict


@app.route('/subscribe/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        r = requests.get(lookupaddr+'/topiclist')
        topiclist = json.loads(r.content)
        return render_template('index.html', topiclist=topiclist)

    else:
        with lock:
            interest_list = request.form.getlist('adcat')
            sid = str(request.sid)
            client_dict[sid] = dict()
            for interest in interest_list:
                client_dict[sid][str(interest)] = dict()
            print interest_list
            return "subscribed!"


@app.route('/region/')
def get_region_polygon():
    with lock:
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
        r = requests.get(lookupaddr+'/region?lat='+str(latitude)+'&lon='+str(longitude))
        publishregion = r.content
        app.logger.debug("Region of publisher: " + str(publishregion))

        sid = str(request.sid)
        interest_list = client_dict[sid].keys()
        for interest in interest_list:
            regions = client_dict[sid][interest].keys()
            new_region_exists = False
            for region in regions:
                if region == publishregion.name:
                    new_region_exists = True
                    client_dict[sid][interest][region][0] = True
                else:
                    client_dict[sid][interest][region][0] = False
                if not new_region_exists:
                    client_dict[sid][interest][publishregion.name] = [True, 0]

    return "region-polygon not yet implemented. But got your region"


@socketio.on('connect')
def handle_connect():
    """
    New connection handler that adds a client to the room list
    :return:
    """
    app.logger.debug('Got a client in room: ' + str(request.sid))
    # with lock:
    #     app.logger.debug('Got a client in room: ' + str(request.sid))
    #     sid = str(request.sid)
    #     # client_dict[sid] = list()


@socketio.on('disconnect')
def handle_disconnect():
    """
    Disconnect handler that removes the client from the room list
    :return:
    """
    with lock:
        sid = str(request.sid)
        client_dict.pop(sid)


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


# def messenger():
#     """
#     Simple stupid test
#     :return:
#     """
#     for i in range(0,100):
#         if len(client_dict) > 0:
#             idx = i % len(client_dict)
#             app.logger.info('Sending message to client in room: ' + str(sidlist[idx]))
#             socketio.emit('server-message', {'data': 'Message sent at time: ' + str(i)}, room=sidlist[idx])
#         app.logger.info('Messenger in iteration: ' + str(i))
#         sleep(5)


if __name__ == '__main__':
    app.debug=True
    # thread = Thread(messenger, ())
    # thread.start()

    socketio.run(app, host="0.0.0.0", port=5200)
