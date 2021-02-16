import json
import random
import time


class level_server:
    QUESTIONS = json.load(open('questions.json', 'r'))
    HIT_PROB = 75
    CHASER_POS = 0
    PLAYER_POS = 0
    HELPING_HAND = 1

    def chaserAnswer(self):
        x = random.randint(1, 100)
        if x > self.HIT_PROB:
            return 0
        return 1

    def updateState(self, money):
        state = "You have "+str(money)+"$"
        if self.HELPING_HAND == 1:
            state += " You still have help available \n"
        else:
            state += " You don't have help available \n"
        for i in range(8):
            state += str(i) + "    "
            if i == self.PLAYER_POS:
                state += "Player"
            if i == self.CHASER_POS:
                state += "Chaser"
            if i == 7:
                state += "Bank"
            state += "\n"
        return state

    def helpFunc(self, correct):
        retHelp = ""
        if self.HELPING_HAND == 1:
            self.HELPING_HAND = 0
            if correct == 1 or correct == 3:
                retHelp = "The answer isn't 2, 4"
            else:
                retHelp = "The answer isn't 1, 3"
        else:
            retHelp = "You have already used your help"
        return retHelp

    def query_question(self, questions):
        # question format:
        # { 'title':
        #   1:
        #   2:
        #   3:
        #   4:
        #   'correct':
        # }
        q = random.choice(questions)
        questions.remove(q)
        # create random permutation
        lst = ['1', '2', '3', '4']
        perm = list()
        for i in range(0, 4):
            a = random.choice(lst)
            lst.remove(a)
            perm.append(a)
        print(perm)
        # select and format
        new_correct = perm.index(q['correct']) + 1
        text = "{}:\n1. {}\n2. {}\n3. {}\n4. {}\n".format(q['title'], q[perm[0]], q[perm[1]], q[perm[2]], q[perm[3]])
        return text, new_correct

    def server_level_1(self, sock):
        score = 0
        for i in range(0, 3):
            # repeat q 3 times...
            text, correct = self.query_question(self.QUESTIONS)
            sock.send(text.encode('utf-8'))
            msg = sock.recv(1024).decode('utf-8')
            try:
                if int(msg) == correct:
                    score += 1
                    sock.send(b"Correct!")
                else:
                    sock.send(b"Wrong!")
            except Exception as e:
                sock.send(b"Invalid option, Wrong answer!")
        return score

    def server_level_2(self, sock):
        multiplier = -1
        msg = sock.recv(1024).decode('utf-8')
        print("msg",msg)
        try:
            if int(msg) == 1:
                multiplier = 1
                self.PLAYER_POS = 3
                sock.send(b"You chose option 1")
            elif int(msg) == 2:
                multiplier = 2
                self.PLAYER_POS = 2
                sock.send(b"You chose option 2")
            elif int(msg) == 3:
                multiplier = 0.5
                self.PLAYER_POS = 4
                sock.send(b"You chose option 3")
            else:
                sock.send(b"Invalid option")
        except Exception as e:
            sock.send(b"Invalid option!")
        return multiplier

    def server_level_3(self, sock, money):
        sock.send(b"begin")
        print(sock.recv(1024))
        while self.PLAYER_POS != 7 and self.PLAYER_POS != self.CHASER_POS:
            text, correct = self.query_question(self.QUESTIONS)
            sock.send(text.encode('utf-8'))
            msg = sock.recv(1024).decode('utf-8')
            try:
                while msg == "help" or msg == "Help":
                    ret = self.helpFunc(correct)
                    sock.send(ret.encode('utf-8'))
                    msg = sock.recv(1024).decode('utf-8')
                if int(msg) == correct:
                    self.PLAYER_POS += 1
                    sock.send(b"Correct!")
                else:
                    sock.send(b"Wrong!")
                self.CHASER_POS += self.chaserAnswer()
            except Exception as e:
                sock.send(b"Invalid option, Wrong answer!")
            mapState = self.updateState(money)
            sock.recv(1024).decode('utf-8')
            sock.send(mapState.encode('utf-8'))
            sock.recv(1024).decode('utf-8')
            if self.PLAYER_POS != 7 and self.PLAYER_POS != self.CHASER_POS:
                sock.send(b"Not done")
            else:
                if self.PLAYER_POS == 7:
                    sock.send(("Congratulations! you have won " + str(money) + "$").encode('utf-8'))
                else:
                    sock.send(b"Congratulations! you have lost to a bot")


class level_client:
    DELAY = 2

    def client_level_1(self, sock):
        msg = "You failed the level, please try again..."
        while msg == "You failed the level, please try again...":
            print("You will be presented with 3 questions, and you have to choose one of the answers (1 to 4)")
            for i in range(0, 3):
                # repeat 3 times
                print("Question: " + str(i + 1))
                print(sock.recv(1024).decode('utf-8'))
                sock.send(input(">>> ").encode('utf-8'))
                print(sock.recv(1024).decode('utf-8'))
                time.sleep(self.DELAY)
            msg = sock.recv(1024).decode('utf-8')
            sock.send(b"OK")
            print(msg)

    def client_level_2(self, sock):
        print("You will be presented with 3 options, and you have to choose one of them (1 to 3)")
        print("1. Begin at stage 3, with the money you earned.")
        print("2. Begin at stage 2, with twice the money you have earned.")
        print("3. Begin at stage 4, with half the money you have earned.")
        sock.send(input(">>> ").encode('utf-8'))
        msg = sock.recv(1024).decode('utf-8')
        print(msg)
        while msg == "Invalid option":
            sock.send(input(">>> ").encode('utf-8'))
            msg = sock.recv(1024).decode('utf-8')
            print(msg)

    def client_level_3(self, sock):
        print(sock.recv(1024).decode('utf-8'), "\n")
        sock.send(b"OK")
        msg = "Not done"
        while msg == "Not done":
            print(sock.recv(1024).decode('utf-8'))
            send = input(">>> ")
            sock.send(send.encode('utf-8'))
            while send == "help" or send == "Help":
                print(sock.recv(1024).decode('utf-8'))
                send = input(">>> ")
                sock.send(send.encode('utf-8'))
            print(sock.recv(1024).decode('utf-8'))
            sock.send(b"Ok")
            time.sleep(self.DELAY)
            print(sock.recv(1024).decode('utf-8'))
            sock.send(b"Ok")
            msg = sock.recv(1024).decode('utf-8')
            time.sleep(self.DELAY)
        print(msg)
