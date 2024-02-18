from wata.file.utils import utils, file_tree_utils # 不能去掉
from pathlib import Path


class FileProcess:

    @staticmethod
    def load_file(path):
        file_ext = Path(path).suffix[1:]
        if file_ext in ['yaml', 'json', 'pkl', 'txt']:
            return eval('utils.load_' + file_ext)(path)
        else:
            raise NameError("Unable to handle {} formatted files".format(file_ext))

    @staticmethod
    def write_file(data, save_path, type):
        if type in ['yaml', 'json', 'pkl', 'txt']:
            return eval('utils.write_' + type)(data, save_path)
        else:
            raise NameError("Unable to handle {} formatted files".format(type))

    @staticmethod
    def free_tree(path, save_txt):
        file_tree_utils.file_tree(path, save_txt)