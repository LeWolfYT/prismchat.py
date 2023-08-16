import Crypto.Cipher.AES as aes
import Crypto.Random as cr
import requests as r
import hashlib as h
import json as j
import time as t
import rsa as rs

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

def login(username: str, password: str, server_addr: str, auth_key=None):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.LOGIN, "params": {"username": username, "password": h.sha256(password)}}]}).json()[0]["status"]

def register(username: str, password: str, server_addr: str, auth_key=None):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.REGISTER, "params": {"username": username, "password": h.sha256(password)}}]}).json()[0]["status"]

def get_key(server_addr: str):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.AUTH_KEY}]}).json()[0]["key"]

def gen_key():
    return rs.encrypt(aes.new())

def send(server_addr: str, author: dict, message: str):
    h = r.post(server_addr, json={"actions": [{"instruction": Instructions.MESSAGE, "params": {"message": {"content": message, "author": author, "timestamp": round(t.time())}}}]}).json()["actions"][0]["status"]
    print(h)
    return h

class Receiver:
    def getAll(self, server_addr: str):
        return r.post(server_addr, json={"actions":[{"instruction": Instructions.READ}]}).json()["actions"][0]["messages"]
    
    def getLatest(self, server_addr: str):
        return self.getAll(server_addr)[-1]

    def getMultiple(self, server_addr: str, count: int):
        return self.getAll(server_addr)[-count::]

rc = Receiver()
if __name__ == "__main__":
    send("http://108.32.95.148:80", {"author": {"pfp": None, "username": "lewolfyt", "displayName": "LeWolfYT", "userID": 404}}, "introducing the new flava")
    for message in rc.getAll("http://108.32.95.148:80"):
        print(message["content"])