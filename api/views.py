from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import json
# import math
# import random
from .nodes import P2PNetwork
import socketio
# import sys
# import integrator
# import subprocess
import pyrebase



firebase_storage = pyrebase.initialize_app(firebaseConfig)
storage = firebase_storage.storage()

# from firebase_admin import db , credentials

# cred = credentials.Certificate("creds.json")
# firebase_admin.initialize_app(cred,{"databaseURL":"https://trustnet-4d788-default-rtdb.asia-southeast1.firebasedatabase.app/"})


def uploadFile2Firebase(filename):
    storage.child(filename).put(filename)

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to Server")
    sio.emit("register","django")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.event
def receive_model(data):
    print(data)
    uploadFile2Firebase("./media/main.py")
    #receive model 
    #store in firebase

real_network = P2PNetwork(6)
dummy_network = P2PNetwork(6)

# print(real_network.add_n_nodes(5))
# print()
# print(real_network.add_n_nodes(2))
# print()
# print(real_network.remove_node('0.1'))
# print()
# print(real_network.get_node_data())
# print()
# print(real_network.get_route('0.1','3'))

@csrf_exempt
def add_dummy_node(request):
    if request.method == "POST":
        global dummy_network
        data = json.loads(request.body)
        val = data.get('val') # from requests - integer
        edges,cordinates , guid_to_address = dummy_network.add_n_nodes(val)
        return JsonResponse({'edges': edges , "cords" : cordinates , "g2a"  : guid_to_address})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def get_dummy_nodes(request):
    global dummy_network
    edges,cordinates , guid_to_address = dummy_network.get_node_data()
    return JsonResponse({'edges': edges , "cords" : cordinates , "g2a"  : guid_to_address})

@csrf_exempt
def get_real_nodes(request):
    global real_network
    edges,cordinates , guid_to_address = real_network.get_node_data()
    return JsonResponse({'edges': edges , "cords" : cordinates , "g2a"  : guid_to_address})

@csrf_exempt 
def remove_dummy_node(request):
    if request.method == "POST":
        global dummy_network
        data = json.loads(request.body)
        val = data.get('id') # id of node on website - string
        edges,cordinates , guid_to_address = dummy_network.remove_node(val)
        return JsonResponse({'edges': edges , "cords" : cordinates , "g2a"  : guid_to_address})
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        file_paths = []
        mpp = {"MLC":request.POST.get("MLC"),"MLS":request.POST.get("MLS")}
        fs = FileSystemStorage()
        addr = request.POST.get("ADDR")
        data = {"no_of_clients" : request.POST.get("NOC") , "ADDR" : addr}
        for file in files:
            filename = fs.save(addr + "_" + file.name, file)
            file_url = fs.url(filename)
            
            proper_url = "media/" + addr + "_" + file.name
            if(mpp["MLS"] == file.name):
                data["ml_server"] = proper_url
            elif(mpp["MLC"] == file.name):
                data["ml_client"] = proper_url
            else:
                data["ml_dataset"] = proper_url

            file_paths.append(file_url)
        print(data)
        # sio.emit("train_model",data)
        return JsonResponse({'message': 'File uploaded successfully!', 'file_urls': file_paths})
    return JsonResponse({'message': 'No file uploaded'}, status=400)


@csrf_exempt
def upload_models(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        file_paths = []
        params = json.loads(request.POST.get("PARAMS"))
        fs = FileSystemStorage()
        data = {}
        for file in files:
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            data["ml_dataset"] = file_url
            file_paths.append(file_url)
        # sio.emit("train_model",data)
        return JsonResponse({'message': 'File uploaded successfully!', 'file_urls': file_paths})
    return JsonResponse({'message': 'No file uploaded'}, status=400)



# sio.connect("http://127.0.0.1:5000")

# def manipulate_string(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         input_string = data.get('string', '')
#         COUNT+=1
#         # Example string manipulation: reverse and uppercase
#         manipulated_string = input_string[::-1].upper()
#         return JsonResponse({'manipulated_string': manipulated_string , "COUNT" : COUNT})
#     return JsonResponse({'error': 'Invalid method'}, status=405)