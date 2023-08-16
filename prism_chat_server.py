import http.server as s
import queue as kyew #ha-ha, i could do stand-up.
import requests as r
import hashlib as h
import json as j
import rsa as rs
import os
q = kyew

messagesq = []
inactive_keys = []
active_keys = {}

dbfile = os.path.join(os.path.realpath(os.path.dirname(__file__)), "db.json")
tmpfile = os.path.join(os.path.realpath(os.path.dirname(__file__)), "tmp.json")

(pkey, rkey) = rs.newkeys(1024)

class Instructions:
    NULL = -0x1
    FALSE = 0x0
    TRUE = 0x1
    PING = 0x2
    LOGIN = 0x3
    WRITE = 0x4
    READ = 0x5
    REPLY = 0x6
    TIME = 0x7
    REGISTER = 0x8
    MESSAGE = 0x9
    EDIT = 0xA
    SET_STATUS = 0xB
    GET_STATUS = 0xC
    USERNAME = 0xD
    PASSWORD = 0xE
    AUTH_KEY = 0xF
    OTHER = 0x10
    NAME = 0x11
    FAILURE = 0x12
    STEVEN = 0x12
    SUCCESS = 0x13
    INVALID = 0x14
    NOT_FOUND = 0x15
    DEFAULT = 0x16
    LOGOUT = 0x17
    ERROR = 0x18
    ACTIVE = 0x19
    RESTRICTED = 0x1A
    COFFEE = 0x1B
    TEA = 0x1C
    IM_A_TEAPOT = 0x1D
    IM_A_COFFEE_POT = 0x1E
    AUTHOR = 0x1F
    SELF_KEY = 0x20
    SELF_KEY_ENCRYPTED = 0x21

class Server(s.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, hmm=messagesq) -> None:
        self.que = hmm
        super().__init__(request, client_address, server)
    def do_GET(self):
        def send_head(code=200, ctype="text/html"):
            self.send_response(code)
            self.send_header("Content-type", ctype)
            self.end_headers()
        
        send_head(code=405)
    
    def run_instruction(self, inst, args):
        print(inst, args)
        match inst:
            case Instructions.NULL:
                return {Instructions.NULL}
            case Instructions.LOGIN:
                if not ("username" in args and "password" in args and "auth_key" in args):
                    return {"status": Instructions.INVALID}
                auth = rs.decrypt(args["auth_key"].encode(), rkey).decode()
                try:
                    un = rs.decrypt(args["username"].encode(), rkey).decode()
                except rs.DecryptionError:
                    return {"status": Instructions.AUTH_KEY}
                except:
                    return {"status": Instructions.ERROR}
                try:
                    ps = rs.decrypt(args["password"].encode(), rkey).decode()
                except rs.DecryptionError:
                    return {"status": Instructions.AUTH_KEY}
                except:
                    return {"status": Instructions.ERROR}
                with open(dbfile, "r") as fil:
                    js = j.loads(fil.read())
                if un in js:
                    if js["account"] == ps:
                        return {"status": Instructions.SUCCESS}
                    else:
                        return {"status": Instructions.FAILURE}
                else:
                    return {"status": Instructions.NOT_FOUND}
            case Instructions.AUTH_KEY:
                return {"status": Instructions.SUCCESS, "key": pkey} #send the public key to the client
            case Instructions.SELF_KEY:
                #the client sent a key
                #add it to the inactive keys
                inactive_keys.append(rs.decrypt(str(args["key"]).encode(), rkey).decode())
            case Instructions.MESSAGE:
                if "message" in args:
                    try:
                        print(f"GOT MESSAGE {rs.decrypt(args['message']['content'], active_keys[args['message']['author']['username']])}")
                    except rs.DecryptionError:
                        return {"status": Instructions.SELF_KEY_ENCRYPTED}
                    self.que.append(args['message'])
                    #print(f"CURRENT KYUWEWE {self.que}")
                    return {"status": Instructions.SUCCESS}
                else:
                    print(f"GOT BAD {args}")
                    return {"status": Instructions.INVALID}
            case Instructions.READ:
                return {"status": Instructions.SUCCESS, "messages": self.que}
            case _:
                return {"status": Instructions.INVALID}

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        def output(jsondt):
            self.wfile.write(bytes(j.dumps(jsondt), encoding="utf-8"))
        
        length = int(self.headers.get('content-length'))
        try:
            data = j.loads(self.rfile.read(length))
        except:
            output({"status": Instructions.INVALID})
            return
        
        if not "actions" in data:
            output({"status": Instructions.INVALID})
            return
        actions = data["actions"]
        
        returnval = {"actions": []}
        
        for action in actions:
            if "params" in action:
                params = action["params"]
            else:
                params = None
            returnval["actions"].append(self.run_instruction(action["instruction"], params))
        
        output(returnval)

port = 8080
port = 5743

iphost = "localhost"
iphost = "192.168.1.172"
try:
    server = s.HTTPServer((iphost, port), Server)
except:
    print("egg")

try:
    server.__setattr__("que", messagesq)
    print("THE SERVER IS ONLINE ON PORT " + str(port))
    server.serve_forever()
except:
    print("egg")