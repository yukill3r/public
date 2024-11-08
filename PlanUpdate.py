import requests
import shutil
import os
import pathlib
import hashlib
import urllib3
import tempfile
from urllib.parse import urlparse
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BUF_SIZE = 65536
URL_TO_PLAN = ''
FILE_NAME = ''
LOCAL_FILE_LOCATION = pathlib.Path('')


class UpdatePlan:
    plan_url = None
    file_name = None
    file_url = None

    def __init__(self, plan_url: str, file_name: str, local_file_on_disk: str):
        self.plan_url = plan_url
        self.file_name = file_name
        self.local_file_on_disk = local_file_on_disk
        self.get_selected_file()
        self.temporary_location = pathlib.Path(
            tempfile.gettempdir()).joinpath(os.path.basename(self.file_url))
        self.download_file()
        sha256_online = self.check_sha256(self.temporary_location)
        sha256_local = self.check_sha256(self.local_file_on_disk)
        if sha256_local != sha256_online:
            print(f'Different sha256:\nlocal = {sha256_local}\nonline = {sha256_online}')
            self.update_file()
        else:
            print(f'sha256:\nlocal = {sha256_local}\nonline = {sha256_online}')
        self.cleanup()

    def get_selected_file(self):
        page = requests.get(self.plan_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            if 'https://ans-gniezno.edu.pl/wp-content/uploads/' in a['href'] and self.file_name in a['href']:
                file_url = a['href']
        
        self.file_url = file_url

    def download_file(self) -> None:
        requested_file = requests.get(self.file_url, allow_redirects=True, verify=False)
        open(self.temporary_location, 'wb').write(requested_file.content)

    def check_sha256(self, file: pathlib.Path) -> str:
        sha256 = hashlib.sha256()
        with open(file, 'rb') as file:
            while True:
                data = file.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
            return sha256.hexdigest()
    
    def update_file(self):
        if os.path.isfile(self.local_file_on_disk):
            os.remove(self.local_file_on_disk)

        if os.path.isfile(self.temporary_location):
            shutil.copy2(self.temporary_location, self.local_file_on_disk.parent)
    
    def cleanup(self):
        if os.path.isfile(self.temporary_location):
            os.remove(self.temporary_location)


if __name__ == '__main__':
    dp = UpdatePlan(URL_TO_PLAN, FILE_NAME, LOCAL_FILE_LOCATION)
