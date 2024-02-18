import sys
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QLabel,QDialog
# from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie, QIcon, QImage, QPainter, QPixmap
import os
import numpy as np
from PyQt5.QtCore import Qt, QTimer
import glob
import random



class MainWindow(QDialog):
    exit_window = QtCore.pyqtSignal()
    def __init__(self,ui,icon,snow,emoji,fireworks):
        super().__init__()
        self.setWindowTitle('Main Window')
        uic.loadUi(ui, self)
        self.setWindowTitle("人生苦短，还好有你！")
        self.setWindowIcon(QIcon(icon))

        # 设置雪花背景
        self.snow_label = QLabel(self)
        self.snow_label.setGeometry(0, 0, self.width(), self.height())
        # print("窗口大小为：", self.width(), self.height())
        snow_gif = QMovie(snow)
        snow_gif.setScaledSize(self.size())
        self.snow_label.setMovie(snow_gif)
        snow_gif.start()

        # 设置退出按钮
        self.ExitButton.setParent(self.snow_label)
        self.ExitButton.clicked.connect(self.exit)

        self.FireButton.setParent(self.snow_label)
        self.FireButton.clicked.connect(self.setting_off_fireworks)

        self.GifLabel.setParent(self.snow_label)

        self.PaiTouLabel.setParent(self.snow_label)
        self.paitou_movie = QMovie(emoji)
        self.paitou_movie.setScaledSize(self.PaiTouLabel.size())
        self.PaiTouLabel.setMovie(self.paitou_movie)
        # paitou_movie.start()

        self.n = 20
        self.all_fireworks = glob.glob(fireworks + '/*.gif')
        # print(self.all_fireworks)
        self.firework_nums = len(self.all_fireworks)
        for i in range(self.firework_nums):
            self.firework_1_movie = QMovie(self.all_fireworks[i])
            setattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie",
                    QMovie(self.all_fireworks[i]))
            for ii in range(self.n):
                setattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii),
                        QMovie(self.all_fireworks[i]))

        self.logoning_movie = QMovie("../img/logoning.gif")

        # 将绘制函数与定时器关联，每隔一段时间更新显示
        self.timer = QTimer()
        self.timer.timeout.connect(self.draw_frames)
        self.timer.start(100)  # 每100毫秒更新一次
        self.nums = []
        for i in range(self.firework_nums):
            self.nums.append(([]))

        # 随机生成 k值
        self.k = self.generate_random_matrix(self.firework_nums, self.n + 1, -300, 450)
        self.c = 0
    def generate_random_matrix(self, m, n, a, b):
        matrix = []
        for i in range(m):
            row = []
            for j in range(n):
                num = random.randint(a, b)
                row.append(num)
            matrix.append(row)
        return matrix
    def draw_frames(self):

        all_frame_list = []
        for i in range(self.firework_nums):
            single_frame_list = []
            single_frame_list.append(
                getattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie").currentPixmap())
            # print(os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie")
            for ii in range(self.n):
                single_frame_list.append(getattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[
                    -1] + "_movie_" + str(ii)).currentPixmap())
                # print(os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii))
            all_frame_list.append(single_frame_list)
        current_frame = self.firework_1_movie.currentFrameNumber()
        # print("当前帧索引：", current_frame)

        width = 900
        height = 450
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        # 使用 QPainter 来绘制图像
        self.painter = QPainter(image)
        for i in range(self.firework_nums):
            for ii in range(self.n + 1):
                if ii in self.nums[i]:
                    self.painter.drawPixmap(self.k[i][ii], 0, all_frame_list[i][ii])

        self.painter.end()
        # 将生成的图像设置给 QLabel 控件进行显示
        self.GifLabel.setPixmap(QPixmap.fromImage(image))

    def init_fireworks(self):
        pass

    def exit(self):
        self.exit_window.emit()
        sys.exit()

    def setting_off_fireworks(self):
        # self.paitou_movie.stop()
        self.paitou_movie.start()
        # print(self.nums)
        # 生成一个随机整数
        i = random.randint(0, self.firework_nums - 1)
        # print("i", i)
        # for i in range(self.firework_nums):  # 相当于 i = 0
        # for ii in range(self.n + 1):
        '''刺激按钮快速反应，我也不知为啥这样，反正这样快一点'''
        if self.c == 0:
            self.firework_1_movie.start()
            self.c = 1
        if self.nums[i] == []:
            self.nums[i].append(0)
            # print("-----------", self.nums)
            getattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie").start()
            return
        for ii in range(self.n):
            # print("------------", ii)
            if ii == self.n - 1:
                self.nums[i] = []
                # print("-----------", self.nums)
                # print(os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii))
                getattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii)).start()
                return
            if np.max(self.nums[i]) == ii:
                self.nums[i].append(ii + 1)
                # print(os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii))
                getattr(self, os.path.splitext(self.all_fireworks[i])[0].split("\\")[-1] + "_movie_" + str(ii)).start()
                return


def app(ui, icon, snow, emoji, fireworks):
    app = QApplication(sys.argv)
    w = MainWindow(ui=ui,
                   icon = icon,
                   snow=snow,
                   emoji=emoji,
                   fireworks=fireworks)
    # 展示窗口
    w.show()
    app.exec()

def open_app(ui, icon, snow, emoji, fireworks):
    print("请输入密码:",end='')
    passward = input()
    if passward == 'wtlovelxq':
        app(ui, icon, snow, emoji, fireworks)
    else:
        print("密码错误")

