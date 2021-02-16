import server
import client


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if input("choose s or c (client or server): ") == 's':
        o = server.Server()
        print("server")
    else:
        o = client.Client()
        print("client")
    o.start()
    print("Would you like to play another game?")
    while input(">>> ") in ["yes", "Yes"]:
        o = client.Client()
        o.start()
        print("Would you like to play another game?")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
