#Kevin Francis Jose
#1001570348
import sys , time
import datetime
import re

#HTTP POST method return the data to be posted

def P_POST (msg):
    header , body = msg.split (';')
    body = body.replace (';','')
    return body

#HTTP GET method return get to data

def G_GET (msg) :
    return 'GET'

#Class Contains HTTP methods and incharge writing and reading http meassage


class HTTP_Request ():

    def __init__(self):
        pass

#encode a request in HTTP

    def encode_HTTP ( msg , method ,ip,port,client):
        message =  method + " /log.txt HTTP/1.1\nHost:" + ip+ "|" + str(port) + "\nUser-Agent:" + str(client) + "\nContent Type:text/plain\nDate:"+str(datetime.datetime.now())+";" + msg
        return message

#Read the HTTP REquests

    def decode_HTTP (msg):
        if msg.find('POST' , 0 , 5) > -1 :
            method = 'POST'
            return P_POST (msg)
        elif msg.find ('GET' , 0 ,5) > -1 :
            method = 'GET'
            return G_GET (msg)
        else :
            return 'error'

#encode the response message to the client

    def response_encode (msg):
        message =  "HTTP/1.1\nContent Type:text/plian\nDate:"+str(datetime.datetime.now())+";" + msg
        return message
#reads the response messages

    def response_decode (msg):
        header , body = msg.split (';')
        body = body.replace (';','')
        return body
