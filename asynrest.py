import socketserver
import json
import sys
sys.path.append('/usr/local/lib/pylib')


from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from threading import Thread
import time
import urllib.parse


class WebServer(socketserver.BaseRequestHandler):
    def createData(self,data):

        if "=" in data:
            data=data.split("=")[1]
            data=urllib.parse.unquote(data)
            return data
        else:
            return "{}"

    def handle(self):
        h=SocketReader(self.request)
        p = HttpStream(h)
        #delagate=url[p.url()]
        delagate=Server.urls[p.url()]
        data = p.body_string()
        if data:
            data=data.decode('utf-8')
        else:
            data=""

        js=None
        data=self.createData(data)
        print(p.url(), data)
        try:
            res=delagate(self.request,data)
            #todo change to:
            # self.request.send(res)
        except Exception as ex:
            print(ex)


class App(socketserver.ThreadingMixIn,socketserver.TCPServer):
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
    def __enter__(self):
        print("server start")
        self.th_serv = Thread(target=self.serve_forever)
        self.th_serv.start()
class Server():
    urls = {}
    def __init__(self,address=("127.0.0.1",7000)):
        self.address=address

    def route(self,url):
        def decorator(f):
            Server.urls[url]=f
            return f
        return decorator

    def run(self):
        with App(self.address,WebServer) as serv:
            while True:
                time.sleep(1)

    def createResponse(self,s, data):
        http = "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{0}"
        j = json.dumps(data)
        http = http.format(j)
        s.send(bytes(http, 'utf-8'))


if __name__ =="__main__":
    app=Server(("0.0.0.0",7000))
    app.run()