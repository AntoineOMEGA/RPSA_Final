from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import json
from urllib.parse import parse_qs, unquote
from db import LocationsDB
from session_store import SessionStore
from http import cookies
from passlib.hash import bcrypt

# HELPER FUNCTIONS


def makeListOfLocations():
    db = LocationsDB()
    locations = db.getLocations()
    return locations


def addNewLocation(location):
    db = LocationsDB()
    location = db.insertLocation()


def checkAuthenticated(self):
    if "userId" not in self.session:
        sendHeaders(self, 401)
        return


def getLocationsHandler(self):
    checkAuthenticated(self)
    db = LocationsDB()
    locationsdict = {"locations": makeListOfLocations()}
    # respond accordingly
    sendHeaders(self, 200)
    self.wfile.write(bytes(json.dumps(locationsdict), "utf-8"))


def getLocationHandler(self):
    checkAuthenticated(self)
    length = self.headers["Path-Length"]
    string = unquote(self.path)
    listed = parse_qs(string)

    parts = string.split("/")
    location_id = parts[2]

    db = LocationsDB()
    location = db.getLocation(location_id)

    if location != None:
        sendHeaders(self, 200)
        self.wfile.write(bytes(json.dumps(location), "utf-8"))
    else:
        sendHeaders(self, 404)
    
def getSessionHandler(self):
    if "userId" not in self.session:
        sendHeaders(self,404)
        return
    sendHeaders(self, 200)


def postLocationsHandler(self):
    checkAuthenticated(self)
    # read the body
    length = self.headers["Content-Length"]
    body = self.rfile.read(int(length)).decode("utf-8")
    string = unquote(body)
    listed = parse_qs(string)

    db = LocationsDB()
    db.insertLocation(listed["title"][0], listed["latitude"][0], listed["longitude"][0], listed["description"][0], listed["category"][0])

    # respond to the client
    sendHeaders(self, 201)

def postUsersHandler(self):
    # REGISTRATION
    db = LocationsDB()

    length = self.headers["Content-Length"]
    body = self.rfile.read(int(length)).decode("utf-8")
    string = unquote(body)
    listed = parse_qs(string)

    isEmailTaken = db.getUser(listed["email"][0])

    if isEmailTaken == False:
        db.insertUser(listed["firstname"][0], listed["lastname"][0], listed["email"][0], bcrypt.hash(listed["password"][0]))
        # respond to the client
        sendHeaders(self, 201)
    else:
        sendHeaders(self, 422)

def postSessionsHandler(self):
    length = self.headers["Content-Length"]
    body = self.rfile.read(int(length)).decode("utf-8")
    string = unquote(body)
    listed = parse_qs(string)

    db = LocationsDB()
    get = db.getUser(listed["email"][0])
    if get == False:
        sendHeaders(self, 404)
    elif bcrypt.verify(listed["password"][0], get[0]["password"]):
        # respond to the client
        user = db.getUser(listed["email"][0])
        sendHeaders(self, 201)
        self.wfile.write(bytes(json.dumps(user), "utf-8"))
        uid = db.getUser(listed["email"][0])
        self.session["userId"] = uid
    else:
        sendHeaders(self, 401)


def deleteLocationHandler(self):
    parts = self.path.split("/")
    location_id = parts[2]

    db = LocationsDB()
    location = db.getLocation(location_id)
    if location != None:
        location = db.deleteLocation(location_id)

        if location == "Deleted":
            sendHeaders(self, 200)
        else:
            sendHeaders(self, 404)


def deleteSessionHandler(self):
    del self.session["userId"]
    sendHeaders(self, 200)


def putLocationHandler(self):
    parts = self.path.split("/")
    location_id = parts[2]

    length = self.headers["Content-Length"]
    body = self.rfile.read(int(length)).decode("utf-8")
    string = unquote(body)
    listed = parse_qs(string)

    db = LocationsDB()
    location = db.getLocation(location_id)
    if location != None:
        location = db.updateLocation(
        location_id, listed["title"][0], listed["description"][0], listed["category"][0])

        if location == "Updated":
            sendHeaders(self, 200)
        else:
            sendHeaders(self, 404)


def sendHeaders(self, status):
    if status == 404:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes("Data Does Not Exist", "utf-8"))
    elif status == 201:
        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes("Created", "utf-8"))
    elif status == 200:
        self.send_response(200)
        self.end_headers()
    elif status == 400:
        self.send_response(400)
        self.end_headers()
        self.wfile.write(bytes("Path Does Not Exist", "utf-8"))
    elif status == 422:
        self.send_response(422)
        self.end_headers()
        self.wfile.write(bytes("Unprocessable", "utf-8"))
    elif status == 401:
        self.send_response(401)
        self.end_headers()
        self.wfile.write(bytes("Failed", "utf-8"))


"""
def handleDeleteMember(self):
    if "userId" not in self.session:
        self.handle401()
        return
    run the rest of the request

    DO NOT PUT THIS ON REGISTRATION OR LOGIN
"""

SESSION_STORE = SessionStore()


class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def load_cookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def send_cookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    def load_session(self):
        self.load_cookie()
        # if session id in cookie
        if "sessionId" in self.cookie:  # sessionId REMEMBER TO WRITE IT THIS WAY
            sessionId = self.cookie["sessionId"].value
            # save session for use later
            self.session = SESSION_STORE.getSession(sessionId)
            # otherwise if session id not in session store
            if self.session == None:
                # create new session
                sessionId = SESSION_STORE.createSession()
                self.session = SESSION_STORE.getSession(sessionId)
                # set new session id for cookie
                self.cookie["sessionId"] = sessionId
        # otherwise if session id not in cookie
        else:
            # create new session
            sessionId = SESSION_STORE.createSession()
            self.session = SESSION_STORE.getSession(sessionId)
            # set new session id for cookie
            self.cookie["sessionId"] = sessionId

    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # LIST
    def do_GET(self):
        self.load_session()
        if self.path == "/locations":
            getLocationsHandler(self)
        elif self.path.startswith("/locations/"):
            getLocationHandler(self)
        elif self.path == "/sessions":
            getSessionHandler(self)
        else:
            sendHeaders(self, 400)

    def do_POST(self):
        self.load_session()
        if self.path == "/locations":
            postLocationsHandler(self)
        elif self.path == "/users":
            postUsersHandler(self)
        elif self.path == "/sessions":
            postSessionsHandler(self)
        else:
            sendHeaders(self, 400)

    def do_DELETE(self):
        self.load_session()
        checkAuthenticated(self)
        if self.path.startswith("/locations/"):
            deleteLocationHandler(self)
        elif self.path == "/sessions":
            deleteSessionHandler(self)
        else:
            sendHeaders(self, 400)

    def do_PUT(self):
        self.load_session()
        checkAuthenticated(self)
        if self.path.startswith("/locations/"):
            putLocationHandler(self)
        else:
            sendHeaders(self, 400)


def run():
    listen = ("127.0.0.1", 8080)
    server = HTTPServer(listen, MyRequestHandler)

    print("Listening...")
    server.serve_forever()


run()
