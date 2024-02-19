from colorama import Fore
import requests, json

headers = {"Content-Type": "application/json"}

class Actions:
    global headers

    def __init__(self, server):
        """
        Initialize Actions object.

        Parameters:
        - server: The server object.
        """
        self.server = server

    def _prepare_request(self, api):
        """
        Prepare request for a specific API.

        Parameters:
        - api: The API endpoint.

        Returns:
        Tuple containing authorization and URL.
        """
        return (self.server.authorization, f"http://{self.server.ip}:{self.server.port}/Actions/{api}")

    def command(self, command):
        """
        Execute a command on the server.

        Parameters:
        - command: The command to execute.

        Returns:
        Response JSON or None.
        """
        authorization, url = self._prepare_request("command")

        data = {"auth": authorization, "command": command}
        responsecommand = requests.post(url, json=data, headers=headers)

        if responsecommand.status_code == 200:
            return responsecommand.json()

        if responsecommand.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")
            return None

    def file_upload(self, file_path, upload_address):
        """
        Upload a file to the server.

        Parameters:
        - file_path: Path to the file to be uploaded.
        - upload_address: The address to upload the file to.

        Returns:
        Response JSON or None.
        """
        authorization, url = self._prepare_request("file_upload")

        files = {'file': open(file_path, 'rb')}
        data = {'address': upload_address, 'auth': authorization}
        responseupload = requests.post(url, files=files, data=data)

        if responseupload.status_code == 200:
            return responseupload.json()

        if responseupload.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")
            return None

    def file_search(self, file_name):
        """
        Search for a file on the server.

        Parameters:
        - file_name: The name of the file to search for.

        Returns:
        Response JSON or None.
        """
        authorization, url = self._prepare_request("file_search")

        print(f"{Fore.YELLOW}[+] The process and processing of this command may take time, please wait. "
              f"(It also depends on the server processing)\n\n{Fore.RESET}")
        data = {"auth": authorization, "file_name": file_name}
        responsesearch = requests.post(url, json=data, headers=headers)

        if responsesearch.status_code == 200:
            return responsesearch.json()

        if responsesearch.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")
            return None

    def file_download(self, full_path):
        """
        Download a file from the server.

        Parameters:
        - full_path: The full path of the file to download.

        Returns:
        File download response or None.
        """
        authorization, url = self._prepare_request("file_download")

        data = {"auth": authorization, "file_name": full_path}
        responsefile_download = requests.post(url, data=json.dumps(data), headers=headers)

        if responsefile_download.status_code == 200:
            return responsefile_download

        if responsefile_download.status_code == 401:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Invalid authorization code {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[!] {Fore.RED}Unknown Error.{Fore.RESET}")
            return None