import asyncio
import websockets as w
import websockets.server as ws
import json
import time
import zlib

api_prefix = "/v1"
print(api_prefix + "/channel/read")

DB_PATH = "/Users/pj/.spieldb/"

channels = {"1": {"messages": [], "users": ["1", "2"]}}
accounts = {"1": "test", "2": "test"}

connections = {}
connect_ids = {}
async def handler(websocket):
    #FUNCTIONS###################################################################################
    
    async def write_to_ch(channel_id, message, sending, opid=None):
        tm = str(time.time())
        crc = zlib.crc32((str(sending) + message["content"] + tm).encode())
        channels[str(channel_id)]["messages"].append({"author": str(sending), "content": message, "timestamp": float(tm), "crc32": crc})
        for user in channels[str(channel_id)]["users"]:
            if user != sending and user in connections:
                await connections[str(user)].send(json.dumps({"id": opid, "data": {"author": str(sending), "content": message, "timestamp": float(tm), "channel": channel_id, "crc32": zlib.crc32(str(sending) + message["content"] + tm)}}))
    
    async def returnst(rtval, opid=None):
        await websocket.send(json.dumps({"id": opid, "status": rtval["status"]}))

    #############################################################################################
    print("new handler")
    try:
        while True:
            message = await websocket.recv()
            print("we got good message!")
            try:
                data = json.loads(message)
                print("the message good json")
                if data["path"] == (api_prefix + "/channel/read"):
                    if str(data["channel"]) in channels:
                        if connect_ids[websocket] in channels[str(data["channel"])]["users"]:
                            returnval = {"status": 200}
                            await websocket.send(json.dumps({"id": data["operation"], "status": returnval["status"], "messages": channels[str(data["channel"])]["messages"][(-data["start"]):(-data["end"] if "end" in data else -1)], "users": channels[str(data["channel"])]["users"]}))
                        else:
                            returnval = {"status": 403}
                            await returnst(returnval, data["operation"])
                    else:
                        returnval = {"status": 400}
                        await returnst(returnval, data["operation"])
                elif data["path"] == (api_prefix + "/channel/write"):
                    if str(data["channel"]) in channels:
                        if connect_ids[websocket] in channels[str(data["channel"])]["users"]:
                            await write_to_ch(int(data["channel"]), data["message"], connect_ids[websocket], data["operation"])
                            returnval = {"status": 200}
                            await returnst(returnval, data["operation"])
                        else:
                            returnval = {"status": 403}
                            await returnst(returnval, data["operation"])
                    else:
                        returnval = {"status": 400}
                        await returnst(returnval, data["operation"])
                elif data["path"] == api_prefix + "/channel/new":
                    pass
                    #call the script that writes to a channel
                elif (data["path"] == api_prefix + "/auth/register"):
                    #call the register code
                    print(message, "wants to register")
                elif (data["path"] == api_prefix + "/auth/login"):
                    if data["username"] in accounts:
                        if accounts[data["username"]] == data["password"]:
                            connections[data["username"]] = websocket
                            connect_ids[websocket] = data["username"]
                            returnval = {"status": 200}
                            await returnst(returnval, data["operation"])
                        else:
                            returnval = {"status": 403}
                            await returnst(returnval, data["operation"])
                    else:
                        returnval = {"status": 400}
                        await returnst(returnval, data["operation"])
                else:
                    returnval = {"status": 404}
                    await returnst(returnval, data["operation"])
            except json.JSONDecodeError:
                print("BAD JSON BAD BAD")
                returnval = {"status": 400}
            print(message, "\"" + data["path"] + "\"")
    except w.ConnectionClosed:
        del connections[connect_ids[websocket]]
        del connect_ids[websocket]

async def main():
    ip = ""
    port = 8001
    async with ws.serve(handler, ip, port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())