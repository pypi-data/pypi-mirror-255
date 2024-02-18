from wata.pointcloud.pcd import PointCloudProcess
from wata.lxq.fireworks_explosion import open_app as open_fireworks
import os
from tabulate import tabulate
from wata import obtain_cur_path


def explain():
    table_list = [
        ['终端命令', '功能'],
        ['wata.show_kitti', '展示kitti数据集第一帧'],
        ['wata.print_name', '打印我的名字'],
        ['wata.lxq.yanhua', '打开烟花']
    ]
    print(tabulate(table_list, headers='firstrow', tablefmt='grid'))


def print_my_name():
    print("wangtao")


def show_kitti():
    cur_path = obtain_cur_path()
    PointCloudProcess.show_pcd(os.path.join(cur_path, "resources/pcd/1000000.bin"))


def fireworks():
    cur_path = obtain_cur_path()
    open_fireworks(ui=os.path.join(cur_path, "resources/fireworks/main.ui"),
                   icon=os.path.join(cur_path, "resources/fireworks/icon.png"),
                   snow=os.path.join(cur_path, "resources/fireworks/snow.gif"),
                   emoji=os.path.join(cur_path, "resources/fireworks/paitou.gif"),
                   fireworks=os.path.join(cur_path, "resources/fireworks/fireworks"))
