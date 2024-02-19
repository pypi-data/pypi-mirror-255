from sqlite3 import connect
from colorama import Fore
import os

FORMAT=".X"
class XSession:
    global FORMAT

    def __init__(self) -> None:
        pass

    @staticmethod
    def Check(name_X):
        if os.path.isfile(name_X + FORMAT):
            return True
        else:
            return False

    @staticmethod
    def create(name_X):
        if XSession.Check(name_X):
            print(f"{Fore.RED}{Fore.YELLOW + name_X + FORMAT} File Already Exists!{Fore.RESET}")
            return False
        else:
            X = connect(name_X + FORMAT)
            Xcursor = X.cursor()
            XQuery = '''
                CREATE TABLE IF NOT EXISTS X (
                    ip TEXT NOT NULL,
                    port TEXT NOT NULL,
                    authorization TEXT NOT NULL,
                    status TEXT NOT NULL
                );
                '''
            Xcursor.execute(XQuery)
            X.commit()
            X.close()
            return True

    @staticmethod
    def insert(name_X, ip, port, authorization):
        if XSession.Check(name_X):
            X = connect(name_X + FORMAT)
            Xcursor = X.cursor()
            XData = [(ip, port, authorization, "OK")]
            XQueryData = '''
                INSERT INTO X (ip, port, authorization, status) 
                    VALUES (?, ?, ?, ?);'''
            Xcursor.executemany(XQueryData, XData)
            X.commit()
            X.close()
            return True
        else:
            print(f"{Fore.RED}{Fore.YELLOW + name_X + FORMAT} File Not Exists!{Fore.RESET}")
            return False
