from wata.image.img import ImageProcess
from wata.pointcloud.pcd import PointCloudProcess
from wata.file.file import FileProcess
import os
def __version__():
    return "0.1.2.6"
def obtain_cur_path():
    return os.path.dirname(os.path.abspath(__file__))