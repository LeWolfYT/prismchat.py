import http.server as s
import requests as r
import hashlib as h
import queue as kyew #ha-ha, i could do stand-up.
import json as j
import rsa as rs
import os
q = kyew

messagesq = []

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
    STATUS = 0xA
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
    RESTRICTED = 0x17
    ERROR = 0x18
    COUNT = 0x19
    NUMBER = 0x1A
    ARRAY = 0x1B
    STRING = 0x1C
    DATA = 0x1D
    AUTHOR = 0x1E
    SELF_KEY = 0x1F
    SELF_KEY_ENCRYPTED = 0x20

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
        match inst:
            case Instructions.NULL:
                return {Instructions.NULL}
            case Instructions.LOGIN:
                un = args["username"]
                ps = args["password"]
                with open(dbfile, "r") as fil:
                    js = j.loads(fil.read())
                if js.has_key(un):
                    if js["un"] == ps:
                        return {"status": Instructions.SUCCESS}
                    else:
                        return {"status": Instructions.FAILURE}
                else:
                    return {"status": Instructions.NOT_FOUND}
            case Instructions.AUTH_KEY:
                return {"status": Instructions.SUCCESS, "key": pkey} #send the public key to the client
            case Instructions.SELF_KEY:
                #the client sent a key
                pass
            case Instructions.MESSAGE:
                print(f"GOT MESSAGE {args['message']}")
                self.que.append(args['message'])
                print(f"CURRENT KYUWEWE {self.que}")
                return {"status": Instructions.SUCCESS}
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
            returnval["actions"].append(self.run_instruction(action["instruction"], action["params"]))
        
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