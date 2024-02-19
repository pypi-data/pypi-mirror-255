from XSession.Session import XSession
from colorama import Fore
import requests

headers = {"Content-Type": "application/json"}

class Server:
    global headers

    def __init__(self, name_X, ip, port, authorization):
        """
        Initialize Server object.

        Parameters:
        - name_X: Name of the XSession.
        - ip: IP address of the server.
        - port: Port of the server.
        - authorization: Authorization of the server.
        """
        self.ip = ip
        self.port = port
        self.authorization = authorization

        XStatus = XSession.Check(name_X)

        if XStatus == False:
            urlSERVER = f"http://{self.ip}:{self.port}/SERVER"
            responseSERVER = requests.post(urlSERVER, headers=headers)

            if responseSERVER.status_code == 200:
                urlAuthorization = f"http://{self.ip}:{self.port}/Account/Authorization"
                data = {"auth": self.authorization}
                responseAuthorization = requests.post(urlAuthorization, json=data, headers=headers)

                if responseAuthorization.status_code == 200:
                    XSession.create(name_X)
                    XSession.insert(name_X, self.ip, self.port, self.authorization)

                elif responseAuthorization.status_code == 401:
                    print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
                else:
                    print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Authorization Error.{Fore.RESET}")
            else:
                print(f"{Fore.RED}[!] {Fore.RED}Server With IP : {Fore.YELLOW}{ip}{Fore.RED} And Port : {Fore.YELLOW}{port}{Fore.RED} Not Found !{Fore.RESET}")

    def get_info_server(self):
        """
        Get information about the server.

        Returns:
        Server information.
        """
        urlget_info_server = f"http://{self.ip}:{self.port}/SERVER/get_info_server"
        data = {"auth": self.authorization}
        responseget_info_server = requests.post(urlget_info_server, json=data, headers=headers)

        if responseget_info_server.status_code == 200:
            return responseget_info_server.json()

        if responseget_info_server.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")

    def get_username(self):
        """
        Get the username associated with the server.

        Returns:
        Username Server.
        """
        urlget_username = f"http://{self.ip}:{self.port}/SERVER/get_username"
        data = {"auth": self.authorization}
        responseget_username = requests.post(urlget_username, json=data, headers=headers)

        if responseget_username.status_code == 200:
            return responseget_username.json()

        if responseget_username.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")
