import os, sys


__version__ = '1.0.8'


class FileManager:
    def __init__(self, app_name: str, developer: str = None):
        self.app_name = app_name
        self.developer = developer
        self.appdata_path = self.get_appdata_path()
        self.create_appdata_path()

    def __repr__(self):
        return f'<FileManager app_name="{self.app_name}" appdata_path="{self.appdata_path}">'

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, key):
        return self.read(key)

    def __setitem__(self, key, value):
        self.write(key, value)

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, key):
        return self.file_exists(key)

    @property
    def path(self):
        return self.appdata_path

    def dir_name(self):
        if self.developer is None:
            return self.app_name

        return f'com.{self.developer}.{self.app_name.lower().replace(" ", "_")}'

    def get_appdata_path(self):
        if sys.platform == 'win32':
            return os.path.join(os.getenv('APPDATA'), self.dir_name())

        if sys.platform == 'darwin':
            return os.path.join(os.getenv('HOME'), 'Library', 'Application Support', self.dir_name())

        if sys.platform == 'linux':
            return os.path.join(os.getenv('HOME'), '.local', 'share', self.dir_name())

        raise NotImplementedError(f'Platform {sys.platform} is not supported.')

    def create_appdata_path(self):
        if not os.path.exists(self.appdata_path):
            os.mkdir(self.appdata_path)

    def set_file(self, filename: str, data: str, encoding: str = 'utf-8'):
        with open(os.path.join(self.appdata_path, filename), 'w', encoding=encoding) as f:
            f.write(data)

    def get_file(self, filename: str, default: str = None, encoding: str = 'utf-8'):
        try:
            with open(os.path.join(self.appdata_path, filename), 'r', encoding=encoding) as f:
                return f.read()

        except FileNotFoundError:
            if default is not None:
                self.set_file(filename, default)
                return default

            raise FileNotFoundError(f'File {filename} does not exist.')

    def set_binary(self, filename: str, data: bytes):
        with open(os.path.join(self.appdata_path, filename), 'wb') as f:
            f.write(data)

    def get_binary(self, filename: str, default: bytes = None):
        try:
            with open(os.path.join(self.appdata_path, filename), 'rb') as f:
                return f.read()

        except FileNotFoundError:
            if default is not None:
                self.write_binary(filename, default)
                return default

            raise FileNotFoundError(f'File {filename} does not exist.')

    def delete_file(self, filename: str):
        os.remove(os.path.join(self.appdata_path, filename))

    def write(self, filename: str, data: str, encoding: str = 'utf-8'):
        self.set_file(filename, data, encoding)

    def read(self, filename: str, default: str = None, encoding: str = 'utf-8'):
        return self.get_file(filename, default, encoding)

    def write_binary(self, filename: str, data: bytes):
        self.set_binary(filename, data)

    def read_binary(self, filename: str, default: bytes = None):
        return self.get_binary(filename, default)

    def remove(self, filename: str):
        return self.delete_file(filename)

    def append(self, filename: str, data: str):
        with open(os.path.join(self.appdata_path, filename), 'a') as f:
            f.write(data)

    def prepend(self, filename: str, data: str):
        with open(os.path.join(self.appdata_path, filename), 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(data.rstrip('\r\n') + '\n' + content)

    def delete_dir(self, dirname: str):
        os.rmdir(os.path.join(self.appdata_path, dirname))

    def file_exists(self, filename: str):
        return os.path.exists(os.path.join(self.appdata_path, filename))

    def create_file(self, filename: str, value: str = ''):
        if not self.file_exists(filename):
            self.set_file(filename, value)

    def create_dir(self, dirname: str):
        if not self.dir_exists(dirname):
            os.mkdir(os.path.join(self.appdata_path, dirname))

    def create_dirs(self, dir_list: list):
        for dirname in dir_list:
            self.create_dir(dirname)

    def dir_exists(self, dirname: str):
        return os.path.exists(os.path.join(self.appdata_path, dirname))

    def create_files(self, file_list: dict):
        for filename, value in file_list.items():
            self.create_file(filename, value)

    def create_folder(self, folder: str):
        self.create_dir(folder)

    def create_folders(self, folders: list):
        self.create_dirs(folders)
