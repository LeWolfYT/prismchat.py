import rsa.randnum as rnd
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

def login(username: str, password: str, server_addr: str, auth_key=None):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.LOGIN, "params": {"username": username, "password": h.sha256(password)}}]}).json()[0]["status"]

def register(username: str, password: str, server_addr: str, auth_key=None):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.REGISTER, "params": {"username": username, "password": h.sha256(password)}}]}).json()[0]["status"]

def get_key(server_addr: str):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.AUTH_KEY}]}).json()[0]["key"]

def send(server_addr: str, author: dict, message: str):
    return r.post(server_addr, json={"actions": [{"instruction": Instructions.MESSAGE, "params": {"message": {"content": message, "author": author, "timestamp": round(t.time())}}}]}).json()[0]["status"]

class Receiver:
    def getAll(self, server_addr: str):
        return r.post(server_addr, json={"actions":[{"instruction": Instructions.READ}]}).json()[0]["response"]
    
    def getLatest(self, server_addr: str):
        return self.getAll(server_addr)[-1]

    def getMultiple(self, server_addr: str, count: int):
        return self.getAll(server_addr)[-count::]