from _socket import _RetAddress
import http.server as s
from socketserver import _RequestType, BaseServer
import requests as r
import hashlib as h
import queue as kyew #ha-ha, i could do stand-up.
import json as j
import rsa as rs
import os
q = kyew

messagesq = q.Queue()

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
    def __init__(self, request: _RequestType, client_address: _RetAddress, server: BaseServer, hmm=None) -> None:
        self.q = hmm
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
                self.q.put(args['message'])
                print(f"CURRENT KYUWEWE {self.q}")
                return {"status": Instructions.SUCCESS}
            case Instructions.READ:
                return {"status": Instructions.SUCCESS}

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        length = int(self.headers.get('content-length'))
        data = j.loads(self.rfile.read(length))
        
        actions = data["actions"]
        
        returnval = {"actions": []}
        
        for action in actions:
            returnval["actions"].append(self.run_instruction(action["instruction"], action["params"]))
        
        output(returnval)
        
        def output(jsondt):
            self.wfile.write(bytes(j.dumps(jsondt), encoding="utf-8"))

port = 8080

iphost = "localhost"
try:
    server = s.HTTPServer((iphost, port), Server)
    server.que = messagesq
    print("THE SERVER IS ONLINE ON PORT " + str(port))
    server.serve_forever()
except:
    pass