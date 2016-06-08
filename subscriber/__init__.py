
__author__ = 'udaymittal'

from flask_socketio import SocketIO, emit, join_room, leave_room, send
from threading import Thread
from flask import Flask, render_template, request
import requests
import json





# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
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

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from time import sleep



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def messenger():
    '''
    Simple stupid test
    :return:
    '''
    for i in range(0,100):
        if len(sidlist) > 0:
            idx = i % len(sidlist)
            app.logger.info('Sending message to client in room: ' + str(sidlist[idx]))
            socketio.emit('server-message', {'data': 'Message sent at time: ' + str(i)}, room=sidlist[idx])
        app.logger.info('Messenger in iteration: ' + str(i))
        sleep(5)

# All clients are assigned a room when they connect, named with the
# session ID of the connection, which can be obtained from request.sid
# Therefore to address a message to a single client, the session ID of the client
# can be used. (request.sid)

sidlist = []
lookupaddr = 'http://0.0.0.0:5000'

@app.route('/subscribe/', methods=['GET', 'POST'])
def index():
    global thread
    if thread is None:
        thread = Thread(target=messenger)
        thread.daemon = True
        thread.start()
    if request.method == 'GET':
        latitude = request.args.get('lat')
        longitude = request.args.get('lon')
        r = requests.get(lookupaddr+'/region?lat='+str(latitude)+'&lon='+str(longitude))
        publishregion = r.content
        app.logger.debug("Region of publisher: " + str(publishregion))

        # request for list of available topics
        r = requests.get(lookupaddr+'/topiclist')
        topiclist = json.loads(r.content)

        return render_template('index.html', topiclist=topiclist)
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



if __name__=='__main__':
    #thread.start_new_thread(messenger, ())
    app.debug = True
    socketio.run(app, port=5200)
