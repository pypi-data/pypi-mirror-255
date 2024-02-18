import keyring
import os
# This is the  key ring of the file it which stores the session and the path 
# where to want to want to store the file and data 
username_cmd = "whoami"
output = os.popen(username_cmd).read()
lnx_name = output.strip()
class Store:
    def __init__(self):
        self.servicename = "SNALABS"
        self.username = "SNALABS"

    def setkey(self, password):
        keyring.set_password(self.servicename, self.username, password)

    def getkey(self):
        if keyring.get_password(self.servicename, self.username):
            return True

    def getsess(self):
        sess = keyring.get_password(self.servicename, self.username)
        return sess
    def getheadless(self):
        try:
            with open(f"/usr/bin/labssession",'r') as f:
                headsession = f.read()
                return headsession
        except:
            return None
    def deletekey(self):
        if keyring.get_password(self.servicename, self.username):
            if keyring.delete_password(self.servicename, self.username):
                return True
        return False
    def deletekey_sess(self):
        try:
            os.remove(f"/home/{lnx_name}/.local/labssession")
        except FileNotFoundError as file:
            print(file)
# obj = Store()
# print(obj.getsess())