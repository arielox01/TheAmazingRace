import socket
import threading


from levels import *

IP = '127.0.0.1'
PORT = 8008
MAX_COUNT = 3


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = list()
        self.threads = list()
        self.done = False
        self.ip = IP
        self.port = PORT
        self.server.bind((IP, PORT))
        self.server.listen(5)

    def accept(self):
        # accept new connections
        while not self.done:
            (conn, addr) = self.server.accept()
            if len(self.clients) >= MAX_COUNT:
                # max conn achieved...
                conn.send(b"ERROR_MAX_CONN")
                conn.close()
            else:
                # validate and and to client list
                conn.send(b"OK")
                self.clients.append(conn)
                # start processing client
                t = threading.Thread(target=self.process, args=[conn])
                self.threads.append(t)
                t.start()

    def process(self, conn):
        try:
            levels = level_server()
            money = 0
            playerPos = 0
            # level 1
            money = 5000*levels.server_level_1(sock=conn)
            while money < 5000:
                # retry...
                conn.send(b"You failed the level, please try again...")
                print(conn.recv(1024))
                money = 5000*levels.server_level_1(sock=conn)
            else:
                conn.send(("You have earned "+str(money)+"$").encode('utf-8'))
                print(conn.recv(1024))
            # level 2
            money = money * levels.server_level_2(sock=conn)
            while money < 0:
                money = money * -1
                money = money * levels.server_level_2(sock=conn)
            # level 3
            levels.server_level_3(sock=conn, money=money)
            msg = conn.recv(1024).decode('utf-8')
            if msg == "Goodbye":
                self.clients.remove(conn)
            else:
                self.process(conn)
        except [ConnectionAbortedError, ConnectionResetError] as e:
            # conn closed...
            self.clients.remove(conn)

    def start(self):
        # start the server
        self.accept()
