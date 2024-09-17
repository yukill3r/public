import requests
import shutil
import os
import pathlib
import hashlib
import urllib3
import tempfile
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BUF_SIZE = 65536
URL_TO_PLAN = ''
LOCAL_FILE_LOCATION = pathlib.Path('')


class UpdatePlan:
    _url = None
    _temporary_location = None
    _local_file_on_disk = None
    _debug = False

    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, url:str):
        self._url = url
    
    @property
    def temporary_location(self):
        return self._temporary_location
    
    @temporary_location.setter
    def temporary_location(self, temp_location:pathlib.Path):
        self._temporary_location = temp_location
    
    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, debug:bool):
        self._debug = debug

    @property
    def local_file_on_disk(self):
        return self._local_file_on_disk
    
    @local_file_on_disk.setter
    def local_file_on_disk(self, local_file_on_disk):
        self._local_file_on_disk = local_file_on_disk
    
    def __init__(self,
                 url: str,
                 local_file_on_disk: pathlib.Path,
                 debug = False):
        self.url = url
        self.local_file_on_disk = local_file_on_disk
        self.debug = debug
        self.temporary_location = pathlib.Path(
            tempfile.gettempdir()).joinpath(os.path.basename(urlparse(self.url).path))

        if self.debug:
            print(f"LocalFile: {self.local_file_on_disk}\nURL:{self.url}\nTemp_Loc:{self.temporary_location}")
        if (self.url == None or self.local_file_on_disk == None or self.temporary_location == None):
            return

        self.DownloadFile()

        sha256_online = self.CheckSHA256(self._Temp_loc)
        sha256_local = self.CheckSHA256(self._Local_File)

        if (sha256_local != sha256_online):
            self.UpdateFile()

        self.Cleanup()


    def DownloadFile(self) -> None:
        requested_file = requests.get(self.url, allow_redirects=True, verify=False)
        open(self.temporary_location, 'wb').write(requested_file.content)

    def CheckSHA256(self, file: pathlib.Path) -> str:
        sha256 = hashlib.sha256()
        with open(file, 'rb') as file:
            while True:
                data = file.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
            return sha256.hexdigest()
    
    def UpdateFile(self):
        if os.path.isfile(self.local_file_on_disk):
            os.remove(self.local_file_on_disk)

        if os.path.isfile(self.temporary_location):
            shutil.copy2(self.temporary_location, self.local_file_on_disk.parent)
    
    def Cleanup(self):
        if os.path.isfile(self.temporary_location):
            os.remove(self.temporary_location)


if __name__ == '__main__':
    dp = UpdatePlan(URL_TO_PLAN, pathlib.Path(LOCAL_FILE_LOCATION))
