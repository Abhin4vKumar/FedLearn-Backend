import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.event
def join_room(sid , room):
    sio.enter_room(sid,room)

@sio.event
def leave_room(sid , room):
    sio.leave_room(sid,room)

@sio.event
def sendTORoom(sid , room , msg):
    sio.emit("rep" , msg , room=room , skip_sid = sid)

@sio.event
def train_model(sid , data):
    print(data)
    sio.emit("receive_model",{"SUCESS_OBJ":1})

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)