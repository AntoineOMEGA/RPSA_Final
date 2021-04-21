import os
import base64


class SessionStore:
    # TODO
    # need a dictionary of dictionaries
    # add a new session to the session store
    # retrieve an existing session from the session store
    # create a new session id

    def __init__(self):
        self.sessions = {}

    def createSession(self):
        newSessionId = self.generateSessionId()
        self.sessions[newSessionId] = {}
        return newSessionId

    def getSession(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        else:
            return None

    def generateSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr
