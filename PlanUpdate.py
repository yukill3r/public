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
URL_TO_PLAN = 'https://ans-gniezno.edu.pl/wp-content/uploads/2024/02/inf-s2-3.pdf'
LOCAL_FILE_LOCATION = pathlib.Path('C:\\Users\\yukiller\\Desktop\\inf-s2-3.pdf')

class UpdatePlan:
    _Url = None
    _Temp_loc = None
    _Local_File = None

    def __init__(self,
                 url: str,
                 local_file: pathlib.Path,
                 DEBUG = False):
        self._Local_File = local_file
        self._Url = url
        self._Temp_loc = pathlib.Path(tempfile.gettempdir()).joinpath(os.path.basename(urlparse(self._Url).path))
        
        if DEBUG:
            print(f"LocalFile: {self._Local_File}\nURL:{self._Url}\nTemp_Loc:{self._Temp_loc}")
        if (self._Url == None or self._Local_File == None or self._Temp_loc == None):
            return

        self.DownloadFile(self._Url, self._Temp_loc)
        sha256_online = self.CheckSHA256(self._Temp_loc)
        sha256_local = self.CheckSHA256(self._Local_File)

        if (sha256_local != sha256_online):
            self.UpdateFile()

        self.Cleanup()

    def DownloadFile(self,
                      url: str,
                      dest_loc: pathlib.Path) -> None:
        requested_file = requests.get(url, allow_redirects=True, verify=False)
        open(dest_loc, 'wb').write(requested_file.content)

    def CheckSHA256(self,
                     file: pathlib.Path) -> str:
        sha256 = hashlib.sha256()
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
            return sha256.hexdigest()

    def UpdateFile(self):
        if os.path.isfile(self._Local_File):
            os.remove(self._Local_File)

        if os.path.isfile(self._Temp_loc):
            shutil.copy2(self._Temp_loc, self._Local_File.parent)

    def Cleanup(self):
        if os.path.isfile(self._Temp_loc):
            os.remove(self._Temp_loc)

if __name__ == '__main__':
    dp = UpdatePlan(URL_TO_PLAN, pathlib.Path(LOCAL_FILE_LOCATION))