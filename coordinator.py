#Kevin Francis Jose
#1001570348
"""Client Code"""
import sys , time
from PyQt5.QtWidgets import QApplication, QWidget , QLineEdit ,QPushButton , QTextEdit , QDialog ,QMessageBox, QAction
from PyQt5.QtGui import QIcon
import socket
from threading import Thread
from socketserver import ThreadingMixIn
from http_request import HTTP_Request

Quitting = False

def getclientname (text):
    msg = text.replace (' has joined the chat!','')
    return msg

def getvotes (text):
    x , y = text.split (':')
    return x , y

#Cal time Difference between messages

def Time_Btw(start , end):
    return end - start

#Build GUI

class Window (QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'GATTALIEFE CHATS'#name of program
        self.left = 50 #starting position
        self.top = 50
        self.width = 500 #size of app
        self.height = 500
        quit = QAction("Quit", self) #handle quitting
        quit.triggered.connect(self.closeEvent)
        self.initUI()

#Create GUI

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('Icon.png'))

#Input TextBox to send message

        self.chatTextField = QLineEdit(self)
        self.chatTextField.resize(480,50)
        self.chatTextField.move(10,400)

#Output TextBox to display recvieed meassge

        self.chatTextField2 = QTextEdit(self)
        self.chatTextField2.resize(480,360)
        self.chatTextField2.move(10,20)
        self.chatTextField2.setReadOnly(True)

#Button to send

        self.btnSend=QPushButton("COMMIT",self)
        self.btnSend.resize(480,30)
        self.btnSend.move(10,460)
        self.btnSend.clicked.connect(self.send)

        self.show()

#close app

    def closeEvent (self,Event):
        msg = QMessageBox.question(self,"QUIT","are Y03 Sug@r",QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            Event.accept()
            Client.close()
            sys.exit()
        else:
            Event.ignore()
            pass



# Send Data to server inirder to be broadcasted

    def send (self) :

        global state

        text = self.chatTextField.text()

        window.chatTextField2.append(state)

        data = 'VOTE_REQUEST:-' + text

        state = 'WAIT'
        window.chatTextField2.append(state)
        #send HTTP request for posting Data

        msg = HTTP_Request.encode_HTTP(data ,'POST' , '127.0.0.9',33000,Client)
        Client.send(msg.encode("utf8"))
        self.chatTextField.setText("")

        window.btnSend.setEnabled(False)


#Class Contain client information for reviecing data on Different thread

class ClientThread(Thread):
    def __init__(self,window):
        Thread.__init__(self)
        self.window=window

#Starts client connects to server and recieves messages in HTTP

    def run(self):

       host = '127.0.0.17' #server ip
       port = 33000 #port number of server
       BUFFER_SIZE = 2048 #buffer size

       global Client

       global state


       New_connection = True

       Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket of client


       try:
           Client.connect((host, port)) #connect to server
       except socket.error as e:
           sys.exit() #connection failed

       #loops until program quits and recieve meassage to posted

       Client.settimeout(1.0)

       while not Quitting:

           if New_connection: #send http request to connect to server
               Client.send (HTTP_Request.encode_HTTP("",'GET',host,port,Client).encode("utf8"))
               New_connection = False


           if state == 'WAIT':
               self.coordinate()

           try:

               msg = Client.recv(BUFFER_SIZE).decode()
               text = HTTP_Request.response_decode(msg)

               if text == 'Greetings from the cave! Now type your name':
                   tmp = HTTP_Request.encode_HTTP('Coordinator', 'POST', '127.0.0.9', 33000, Client)
                   Client.send(tmp.encode('utf8'))

               if ' has joined the chat!' in text:
                   clientlist.append(getclientname(text))

           except socket.timeout :
               pass



    def coordinate (self):
        global state
        votes = list() #vate list
        Client.settimeout(30.0) #timeout
        abort = False
        while True: #wait for message
            try:
                msg = Client.recv(2048).decode()
                text = HTTP_Request.response_decode(msg)
                x, y = getvotes(text)
                votes.append(y)
                if len(votes) == len(clientlist): #exit
                    break

            except socket.timeout:
                abort = True
                window.chatTextField2.append('Timeout')
                break

        Client.settimeout(1.0)

        for vote in votes: #check if anyone aborted
            if vote == 'ABORT':
                abort = True

        if abort: #global abort
            msg = HTTP_Request.encode_HTTP('GLOBAL_ABORT', 'POST', '127.0.0.9', 33000, Client)
            Client.send(msg.encode('utf8'))
            state = 'ABORT'
            open('coordinator.txt', "a+").writelines('\nGLOBAL_ABORT')
            window.chatTextField2.append(state)
        else: #global commit
            msg = HTTP_Request.encode_HTTP('GLOBAL_COMMIT', 'POST', '127.0.0.9', 33000, Client)
            Client.send(msg.encode('utf8'))
            state = 'COMMIT'
            open('coordinator.txt', "a+").writelines('\nGLOBAL_COMMIT')
            window.chatTextField2.append(state)
        state = 'INIT'
        window.btnSend.setEnabled(True)
        return
#Program starts here

if __name__ == '__main__':

    clientlist = list()
    text=open('coordinator.txt').read()
    state = 'INIT'
    app = QApplication(sys.argv)
    window = Window()
    window.chatTextField2.setPlainText(text)
    clientThread=ClientThread(window)
    clientThread.start()
    sys.exit(app.exec_())
