#Kevin Francis Jose
#1001570348
"""Server Program for chat room"""
import sys , time
from PyQt5.QtWidgets import QApplication, QWidget , QLineEdit ,QPushButton , QTextEdit , QDialog , QMessageBox , QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import socket
from threading import Thread
from socketserver import ThreadingMixIn
from http_request import HTTP_Request

#Broadcast meassge to all clients

def broadcast(msg,client):  # prefix is for name identification.
    for sock in clients:
        if sock != client:
            sock.send(msg)

#take name and check if it is bad or not

def name_checker (name):
    if len (name) > 15:
        return False
    for names in clients :
        if names == name :
            return False
    return True

#Client Handle function are here program is Multithreaded


#handle information to and from client in a thread

def handle_client (client):

    global coordinator

    bad_name = "Name Enter Is Bad"

    checked = False

    text = client.recv(2048).decode("utf8")

    name = HTTP_Request.decode_HTTP(text) #Data is mostly send as http post method

    #loop till valid client name is found

    while not checked :
        if name_checker (name) :
            checked = True
        else :
            client.send(bytes(HTTP_Request.response_encode(bad_name) , "utf8"))
            name = client.recv(2048).decode("utf8")
            #add to the list of clients
    if name == 'Coordinator':
        coordinator = client
    clients[client] = name
    #welcome message
    welcome = HTTP_Request.response_encode('Welcome %s! If you ever want to quit, type :quit to exit.' % name)

    client.send(bytes(welcome, "utf8")) #send to client
    msg = HTTP_Request.response_encode("%s has joined the chat!" % name)

    broadcast(bytes(msg, "utf8"),client) #broadcast clients arrival

    window.chatTextField2.append (str(text))
    window.chatTextField2.append (str(name))
    #loop till client leave server
    while True:
        request = client.recv(2048).decode('utf8')
        msg = HTTP_Request.decode_HTTP(request)
        #check if the clients wants to leave

        if ":quit" in msg: #leaves server
            client.close() #close client
            del clients[client] #remove from client list
            if not clients:
                break
        else :
            if clients[client]=='Coordinator' :
                broadcast(bytes(HTTP_Request.response_encode(name +":" + msg ), 'utf8'),client)
                window.chatTextField2.append (name + "\n" + request)
            else:
                coordinator.send(HTTP_Request.response_encode(name +":" + msg ).encode('utf8'))
                window.chatTextField2.append(name + "\n" + request)
    return

#Build GUI

class Window (QDialog) :

    def __init__ (self) :
        super().__init__() #creates GUI
        self.title = 'GATTALIEFE CHAT'
        self.left = 250 #Staring Psition
        self.top = 250
        self.width = 500 #Size
        self.height = 500
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.initUI()

    def initUI(self):#define GUI PArameters

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('icon.png'))

#Display HTTP REsquests and Response send to SERVER

        self.chatTextField2 = QTextEdit(self)
        self.chatTextField2.resize(480,400)
        self.chatTextField2.move(10,20)
        self.chatTextField2.setReadOnly(True)

#Button Write Information to a yourfile

        self.btnSend=QPushButton("Join",self)
        self.btnSend.resize(480,30)
        self.btnSend.move(10,460)
        self.btnSend.clicked.connect(self.start_server)

        self.show()


    def closeEvent (self,Event):
        msg = QMessageBox.question(self,"QUIT","are Y03 Sug@r",QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            Server.close()
            Event.accept()
            sys.exit()
        else:
            Event.ignore()
            pass

#Function Writes information to a File
    def start_server (self):
        with open('log.txt' , 'w') as yourfile:
            yourfile.write (str(self.chatTextField2.toPlainText()))

#Contains code Used to Opertaed Server

class ServerThread (Thread):

    def __init__(self,window) :
        Thread.__init__(self)
        self.window = window

#bind SERVER to socket and listen to max of 4 clients and run them on separate threads

    def run(self):
       host = '127.0.0.17' #host ip address
       port = 33000 #host port number
       BUFFER_SIZE = 2048 #string buffer size for recv function
       max_client = 4 #max_no_of_client

       global Server

       Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates server socket
       Server.setsockopt (socket.SOL_SOCKET ,socket.SO_REUSEADDR ,1)

       Server.bind ((host , port)) #binds sockets

       window.chatTextField2.append("STARTED SERVER")

       Server.listen (max_client) #listen to Clients

       window.chatTextField2.append("Waiting For Clients")

       #Listen for Clients
       while True:

           client, client_address = Server.accept() #accept client
           window.chatTextField2.append ("%s:%s has connected." % client_address)
           msg = client.recv(2048).decode("utf8")#client send a HTTP requests

           if HTTP_Request.decode_HTTP(msg) != 'GET':#check HTTP method
               window.chatTextField2.append (msg)
               continue

           welcome = HTTP_Request.response_encode("Greetings from the cave! Now type your name")
           #server send back HTTP response
           window.chatTextField2.append (welcome)

           client.send((welcome).encode( "utf8"))

           addresses[client] = client_address
           newthread = Thread(target= handle_client , args = (client,)) #creates new thread
           newthread.start() #stats new thread

           #displays thread on server gui
           window.chatTextField2.append ("\nTHREAD : " + str(newthread) + "\n")
           thread[client] = newthread #appends to thread list

    #joins child thhread to parent thread

       time.sleep (1)

       #closes server
       Server.close()

#add messages to GUI

       def message (self , msg):
           window.chatTextField2.append (msg)
           return

#Program Start here

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    coordinator = None
    text=open('log.txt').read()
    window.chatTextField2.setPlainText(text)
    serverThread = ServerThread (window)
    clients = {} #list of Clients
    addresses = {} #address of clients
    thread = {} #thread list of threads
    serverThread.start()
    #window.exec()
    sys.exit(app.exec_())
