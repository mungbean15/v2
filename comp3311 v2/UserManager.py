# File with methods and class to manage all users to server

from typing import Dict
from time import time

class UserManager:
    def __init__(self):
        self.__users_map: Dict[str, UserManager.__User] = dict()
        self.__read_credentials()
    
    def __read_credentials(self):
        try:
            with open("credentials.txt", "r") as f_credentials:
                for account in f_credentials:
                    username, password = account.strip().split()
                    self.__users_map[username] = UserManager.__User()
        except:
            print("===== Error: cannot read credentials.txt =====")
            exit(1)

    def authenticate(self, user_input: str, pass_input: str):
        if user_input not in self.__users_map:
            return "===== Error: username does not exist ====="

        return self.__users_map[user_input].authenticate(pass_input)

    def has_user(self, username):
        return username in self.__users_map

    def get_users(self) -> set:
        online_users = set()
        for user in self.__users_map:
            if self.__users_map[user].is_online():
                online_users.add(user)
        return online_users
    

    
    class __User:
        def __init(self, username: str, password: str):
            self.__username: str = username
            self.__password: str = password
            self.__online: bool = False
            self.__blocked: bool = False
            self.__block_timeout: int = 10
            self.__blocked_since: int = 0
            self.__login_time: int = int(time())
            self.__private_port: int = 0
            self.__consecutive_fails: int = 0
        
        def set_private_port(self, port: int):
            self.__private_port = port
        
        def get_private_port(self):
            return self.__private_port
        
        def update(self):
            if self.__blocked and self.__blocked_since + self.__block_timeout < time():
                self.__blocked = False

        def is_online(self):
            return self.__online
        
        def login_time(self):
            return self.__login_time
        
        def authenticate(self, pass_input: str):
            if self.__online:
                return "===== User is already logged in ====="
            if self.__password != pass_input:
                self.__consecutive_fails += 1
                if self.__consecutive_fails >= 5:
                    self.__blocked_since = time()
                    self.__blocked = True
                    return "===== Error: invalid password, you are blocked ======"
                return "===== Error: your password in incorrect ====="
                # you can add how many attempts left
            
            # successful login:
            self.__online = True
            self.login_time = int(time())
            return "===== You have successfully logged in ====="