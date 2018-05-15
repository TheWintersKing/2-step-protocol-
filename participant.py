#Kevin Francis Jose
#1001570348
"""Client Code"""
import sys , time
from PyQt5.QtWidgets import QApplication, QWidget , QLineEdit ,QPushButton , QTextEdit , QDialog , QVBoxLayout , QMessageBox , QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import socket
from threading import Thread
from socketserver import ThreadingMixIn
from http_request import HTTP_Request

Quitting = False

def getmessage (text):
    x , y = text.split(':-')
    return y

#Cal time Difference between messages

def Time_Btw(start , end):
    return end - start

#Build GUI

#login screen

class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.textName = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        self.accept()

class Window (QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'GATTALIEFE CHATS'#name of program
        self.left = 50 #starting position
        self.top = 50
        self.width = 500 #size of app
        self.height = 500
        self.start = 0.0 #start time
        quit = QAction("Quit", self)
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

#Button to commit

        self.btnCommit=QPushButton("COMMIT",self)
        self.btnCommit.resize(100,30)
        self.btnCommit.move(140,460)
        self.btnCommit.clicked.connect(self.commit)

#Button to abort

        self.btnAbort=QPushButton("ABORT",self)
        self.btnAbort.resize(100,30)
        self.btnAbort.move(260,460)
        self.btnAbort.clicked.connect(self.abort)

        self.show()

#commit event

    def commit (self):
        self.send('COMMIT')

    def abort (self):
        self.send('ABORT')

# Send Data to server inirder to be broadcasted

    def send (self , text) :

        global state

        data = text

        #send HTTP request for posting Data

        msg = HTTP_Request.encode_HTTP(data ,'POST' , '127.0.0.9',33000,Client)
        Client.send(msg.encode("utf8"))
        self.chatTextField.setText("")

        if text == 'ABORT':
            state = text
            window.chatTextField2.append(state)
            open(filename,'a+').write('\nVOTE_ABORT')

        else :
            state = 'READY'
            window.chatTextField2.append(state)
            open(filename, 'a+').write('\nVOTE_COMMIT')


        window.btnAbort.setEnabled(False)
        window.btnCommit.setEnabled(False)


    def closeEvent (self,Event):
        msg = QMessageBox.question(self,"QUIT","are Y03 Sug@r",QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            Client.close()
            Event.accept()
            sys.exit()
        else:
            Event.ignore()
            pass

#Class Contain client information for reviecing data on Different thread

class ClientThread(Thread):
    def __init__(self,window):
        Thread.__init__(self)
        self.window=window

#Starts client connects to server and recieves messages in HTTP

    def run(self):
       global state
       host = '127.0.0.17' #server ip
       port = 33000 #port number of server
       BUFFER_SIZE = 2048 #buffer size
       global Client

       New_connection = True

       Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket of client

       try:
           Client.connect((host, port)) #connect to server
       except socket.error as e:
           sys.exit() #connection failed
       #loops until program quits and recieve meassage to posted

       Client.settimeout(60.0)


       while not Quitting:

           if New_connection: #send http request to connect to server
               Client.send (HTTP_Request.encode_HTTP("",'GET',host,port,Client).encode("utf8"))
               New_connection = False

           if state == 'READY':
               self.part(attr)

           try:
               msg = Client.recv(BUFFER_SIZE).decode()
               text = HTTP_Request.response_decode(msg)



#decision request handling

               if 'DECISION_REQUEST' in text:
                    if state == 'INIT' or state == 'ABORT':
                        msg = HTTP_Request.encode_HTTP('DECISION_REQUEST GLOBAL_ABORT', 'POST', '127.0.0.9', 33000, Client)
                        Client.send(msg.encode("utf8"))
                    if state == 'COMMIT':
                        msg = HTTP_Request.encode_HTTP('DECISION_REQUEST GLOBAL_COMMIT', 'POST', '127.0.0.9', 33000, Client)
                        Client.send(msg.encode("utf8"))
                    else:
                        msg = HTTP_Request.encode_HTTP('DECISION_REQUEST dafdfgfd', 'POST', '127.0.0.9', 33000, Client)
                        Client.send(msg.encode("utf8"))

#if new
               if text == 'Greetings from the cave! Now type your name':
                   tmp = HTTP_Request.encode_HTTP(login.textName.text() ,'POST' , '127.0.0.9',33000,Client)
                   Client.send(tmp.encode('utf8'))

               window.chatTextField2.append(text)


               if 'Coordinator:' in text:
                   if 'VOTE_REQUEST:-' in text:
                       state ='INIT'
                       window.chatTextField2.append(state)
                       open(filename,'a+').write('\n'+state)
                       attr = getmessage(text)
                       window.btnAbort.setEnabled(True)
                       window.btnCommit.setEnabled(True)
                   else:
                       if self.action(attr, text):
                           window.btnAbort.setEnabled(False)
                           window.btnCommit.setEnabled(False)
                           pass

           except socket.timeout:
               window.chatTextField2.append('VOTE_ABORT')
               open(filename, 'a+').write('\nVOTE_ABORT')
               pass

#ready state
    def part (self,attr):
        global  state
        Client.settimeout(30.0)
        while True:
            try:
                msg = Client.recv(2048).decode()
                text = HTTP_Request.response_decode(msg)

                if 'Coordinator:' in text:
                    if self.action(attr, text):
                        break
                    window.btnAbort.setEnabled(False)
                    window.btnCommit.setEnabled(False)

            except socket.timeout:
                window.chatTextField2.append('timeout')
                Client.settimeout(None)
                self.decision (attr)
                break
        Client.settimeout(1.0)

#wait for decision
    def decision (self,attr):
        global state
        msg = HTTP_Request.encode_HTTP('DECISION_REQUEST','POST' , '127.0.0.9',33000,Client)
        Client.send(msg.encode("utf8"))
        while True:
            try:
                msg = Client.recv(2048).decode()
                text = HTTP_Request.response_decode(msg)
                if self.action(attr,text):
                    window.btnAbort.setEnabled(False)
                    window.btnCommit.setEnabled(False)
                    break
            except socket.timeout :
                pass

#check action
    def action (self,attr ,text):
        global state
        if 'GLOBAL_COMMIT' in text:
            state = 'COMMIT'
            window.chatTextField2.append('GLOBAL_COMMIT')
            window.chatTextField2.append(attr)
            open(filename, 'a+').write('\n' + attr + '\nGLOBAL_COMMIT')
            return True
        if 'GLOBAL_ABORT' in text:
            state = 'ABORT'
            window.chatTextField2.append('GLOBAL_ABORT')
            open(filename, 'a+').write('\n' + attr + '\nGLOBAL_ABORT')
            return True
        if 'error' in text:
            state = 'ABORT'
            window.chatTextField2.append('GLOBAL_ABORT')
            open(filename, 'a+').write('\nGLOBAL_ABORT')
            window.btnAbort.setEnabled(False)
            window.btnCommit.setEnabled(False)
            return True
        return False

    def get_last (self):
        with open(filename) as f:
            data = f.read()
        x = list(data.split('\n'))

        return x[-1]

#Program starts here

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    if login.exec_() == QDialog.Accepted:
        state = 'INIT'
        window = Window()
        filename = login.textName.text()+'.txt'
        try:
            text = open(filename, 'r+').read()
        except :
            text = open(filename, 'w+').read()
        window.btnAbort.setEnabled(False)
        window.btnCommit.setEnabled(False)
        window.chatTextField2.setPlainText(text)
        clientThread=ClientThread(window)
        clientThread.start()
        sys.exit(app.exec_())
