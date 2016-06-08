async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from time import sleep
import requests
from threading import Thread, Lock
import json

__author__ = 'udaymittal'

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None


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
kafkadrr = 'http://192.168.43.154:5000/poll/'


def collect_topics():
    topic_dict = dict()
    app.logger.debug("Inside Collected Topics - Number of connected clients: " + str(len(client_dict)))
    for sid in client_dict.keys():
        for interest in client_dict[sid].keys():
            for region in client_dict[sid][interest].keys():
                if client_dict[sid][interest][region][0]:
                    topic = interest + '_' + region
                    try:
                        if client_dict[sid][interest][region][1] < topic_dict[topic]:
                            topic_dict[topic] = client_dict[sid][interest][region][1]
                    except KeyError:
                        topic_dict[topic] = client_dict[sid][interest][region][1]
    app.logger.debug("Topic Dict: " + str(topic_dict))
    return topic_dict


def poll_topics():
    topic_dict = collect_topics()
    ads = requests.post(kafkadrr, json=json.dumps(topic_dict))
    app.logger.debug("Received Ads: " + str(ads.content))
    return json.loads(ads.content)


def messenger():
    while True:
        sleep(5)
        app.logger.debug("Inside Messenger Iteration")
        msgs = poll_topics()
        ads = dict()
        for topic in msgs.keys():
            all_msgs = msgs[topic]
            ads[topic] = dict()
            for msg in all_msgs:
                offset = msg[2]
                ad = msg[-1]
                ads[topic][offset] = ad
            # offset = msg.offset
            # ad = msg.value
            # try:
            #     ads[topic][offset] = ad
            # except KeyError:
            #     ads[topic] = dict
            #     ads[topic][offset] = ad

        for sid in client_dict.keys():
            interest_list = client_dict[sid].keys()
            for interest in interest_list:
                regions = client_dict[sid][interest].keys()
                for region in regions:
                    if client_dict[sid][interest][region][0]:
                        offset = client_dict[sid][interest][region][1]
                        while True:
                            try:
                                ad = ads[interest+'_'+region][offset]
                                socketio.emit('server-message', ad, room=sid)
                                offset += 1
                            except KeyError:
                                break


@app.route('/subscribe/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        r = requests.get(lookupaddr+'/topiclist')
        topiclist = json.loads(r.content)
        return render_template('index.html', topiclist=topiclist)

    else:
        with lock:
            interest_list = request.form.getlist('adcat')
            sid = str(request.headers.get('sid'))
            client_dict[sid] = dict()
            for interest in interest_list:
                client_dict[sid][str(interest)] = dict()
            print interest_list
            return "subscribed!"


@app.route('/subscribe/region')
def get_region_polygon():
    with lock:
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
        r = requests.get(lookupaddr+'/region?lat='+str(latitude)+'&lon='+str(longitude))
        publishregion = r.content
        print publishregion
        publishregion = json.loads(publishregion)
        app.logger.debug("Region of publisher: " + str(publishregion))
        # print publishregion
        # print type(publishregion)
        # print publishregion['name']
        sid = str(request.headers.get('sid'))
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
                client_dict[sid][interest][publishregion['name']] = [True, 0]

    print client_dict
    return str(publishregion['polygon'])


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
    app.logger.debug("Client disconnected: " + str(request.sid))
    with lock:
        sid = str(request.sid)
        try:
            client_dict.pop(sid)
        except KeyError:
            pass


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
#             app.logger.info('Sending message to client in room: ')
#             socketio.emit('server-message', {'data': 'Message sent at time: ' + str(i)})
#         app.logger.info('Messenger in iteration: ' + str(i))
#         sleep(5)
#

if __name__ == '__main__':
    app.debug = True
    thread = Thread(target=messenger)
    thread.daemon = True
    thread.start()

    socketio.run(app, host="0.0.0.0", port=5200)
