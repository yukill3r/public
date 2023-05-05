import shutil
import pathlib
import glob
import os
import pyunpack
import stat

os.chdir(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_EXTRACT = r'C:\Test\sorter\files_to_extract'
LOCATION_TO_EXTRACT = r'C:\test\sorter\files_extracted'

class sort_and_modify:
    #region unpack
    def main_loop_extract(self):
        print('Start unzip')
        files_to_extract = glob.glob(str(FILES_TO_EXTRACT) + '\*.*', recursive=True)
        for file in files_to_extract:
            try:
                self.unzipper(file, LOCATION_TO_EXTRACT)
            except:
                continue
        print('Unzip done')

    def unzipper(self, file:str, extract_dir:str) -> None:
        extract_dir_extended = os.path.join(extract_dir,pathlib.Path(file).stem)
        if not os.path.isdir(extract_dir_extended):
            os.mkdir(extract_dir_extended)
        pyunpack.Archive(file).extractall(extract_dir_extended)
    #endregion

    #region sorter
    def main_loop_sorter(self):
        for dir_name in os.listdir(LOCATION_TO_EXTRACT):
            path_pure = pathlib.Path.joinpath(pathlib.Path(LOCATION_TO_EXTRACT), dir_name)

            glob_list = glob.glob(str(path_pure) + '\**\*.*', recursive=True)
            
            try:
                for file in glob_list:
                    file = pathlib.Path(file)
                    if not file.parent == path_pure:
                        shutil.move(file, path_pure.joinpath(file.name))
            except:
                continue

            #self.remove_empty_folders(path_pure)

    #todo permission 5 error
    """
    def remove_empty_folders(self, path_abs):
        return 0
        walk = list(os.walk(path_abs))
        for path, _, _ in walk[::-1]:
            if len(os.listdir(path)) == 0:
                os.chmod(path, 0o700)
                os.remove(path)
    """
    #endregion

if __name__ == '__main__':
    sm = sort_and_modify()
    sm.main_loop_extract()
    sm.main_loop_sorter()
