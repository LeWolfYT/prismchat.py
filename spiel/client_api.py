import asyncio
import websockets.sync.client as wsc
import json
import time
ip = "localhost"
port = 8001

def hello():
    with wsc.connect(f"ws://{ip}:{port}") as websocket:
        websocket.send(json.dumps({"path": "/v1/auth/login", "username": "1", "password": "test"}))
        print(json.loads(websocket.recv())["status"])
        websocket.send(json.dumps({"path": "/v1/channel/write", "channel": 1, "message": {"content": f"Hello, world at {time.time()}!"}}))
        message = websocket.recv()
        print(f"Received 1: {message}")
        websocket.send(json.dumps({"path": "/v1/channel/read", "channel": 1}))
        message = websocket.recv()
        print(f"Received 2: {message}")

hello()