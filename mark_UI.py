import cv2
import sys
import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from init import *
import threading
from PyQt5.QtCore import *
from function import *
from qtpy.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPainter
from window_size import *
import pickle
import copy

window_width, window_height = get_window_size()

thumbnail_label_width = int(window_width * 9 / 10)
thumbnail_label_height = int(window_height * 1 / 8)

rect_width = int(window_width * 3 / 4)

id, dll = init()
all_point = []
tmp_point = []
all_mark_text = []
tmp_all_mark_text = []
tmp_all_point = []
tmp_mark_text = []
tmp_tmp_point = []
tmp_tmp_mark_text = []
ratio = 0
original_img_height = 0
original_img_width = 0
control_button_height = 64
control_button_width = 64
thumbnail_x = 0
all_start = 0
all_end = 0
all_start_list = []
hide_mark_state = 0
buffer = ''


class VideoThread(QThread):

    signal = pyqtSignal()

    def __init__(self):
        super(VideoThread, self).__init__()

    def run(self):
        cap = cv2.VideoCapture('rtsp://iot02:iot2015128@192.168.134.122:554//Streaming/Channels/1')
        #cap = cv2.VideoCapture(0)
        if cap.isOpened():
            rval, frame = cap.read()
            print('ture')
        else:
            rval = False
            print('False')
        # 循环使用cv2的read()方法读取视频帧
        while rval:
                rval, frame = cap.read()
                show_image = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2RGB)
                video_image = QImage(show_image.data, show_image.shape[1], show_image.shape[0], QImage.Format_RGB888)
                global buffer
                buffer = video_image
                self.signal.emit()
        cap.release()
        cv2.destroyAllWindows()

class ImageLabel(QLabel):

    def __init__(self, parent=None):
        self.point_start_x = 0
        self.point_start_y = 0
        self.point_end_x = 0
        self.point_end_y = 0
        self.flag_start = True
        super(ImageLabel, self).__init__(parent)

    def paintEvent(self, event):
        QLabel.paintEvent(self, event)
        painter = QPainter()
        painter.begin(self)
        global tmp_point
        if len(tmp_point) > 1:
            pen = QPen(Qt.red, 4, Qt.DashDotLine)
            painter.setPen(pen)

            self.point_start_x = tmp_point[0][0]
            self.point_start_x = tmp_point[0][1]

            for k in range(0, len(tmp_point)):
                if (k + 1) != len(tmp_point):
                    if tmp_point[k][0] == -1 or tmp_point[k + 1][0] == -1:
                        continue
                    else:
                        painter.drawLine(tmp_point[k][0], tmp_point[k][1], tmp_point[k + 1][0], tmp_point[k + 1][1])

        global tmp_mark_text
        if len(tmp_mark_text):
            pen = QPen(Qt.yellow, 8, Qt.SolidLine)
            painter.setPen(pen)

            for l in range(0, len(tmp_mark_text)):
                painter.drawText(tmp_mark_text[l][0], tmp_mark_text[l][1], tmp_mark_text[l][2])
        painter.end()


    def mouseReleaseEvent(self, event):

        global_point = event.globalPos()
        local_point = self.mapFromGlobal(global_point)
        if self.flag_start is True:
            self.point_start_x = local_point.x()
            self.point_start_y = local_point.y()
            global tmp_point
            tmp_point.append([self.point_start_x, self.point_start_y])
            self.flag_start = False
        else:
            self.point_end_x = local_point.x()
            self.point_end_y = local_point.y()
            tmp_point.append([self.point_end_x, self.point_end_y])
            self.flag_start = True
        self.update()

class myLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        global_point = event.globalPos()
        local_point = self.mapFromGlobal(global_point)
        global thumbnail_x
        thumbnail_x = local_point.x()
        self.clicked.emit()

class MarkWindow(QWidget):

    def __init__(self):
        super().__init__()

        # set exit button
        self.exit_button = QPushButton(self)
        self.exit_button.setIcon(QIcon("./icon/quit.png"))
        self.exit_button.setShortcut('Ctrl+Q')
        self.exit_button.setFixedHeight(32)
        self.exit_button.setFixedWidth(32)
        self.exit_button.setToolTip("Quit APP")
        self.exit_button.clicked.connect(qApp.quit)


        # set open button
        self.open_button = QPushButton(self)
        self.open_button.setIcon(QIcon("./icon/open.png"))
        self.open_button.setShortcut('Ctrl+O')
        self.open_button.setFixedHeight(32)
        self.open_button.setFixedWidth(32)
        self.open_button.setToolTip("Open Image")
        self.open_button.clicked.connect(self.open_image)
        self.image_name = ''

        # set save button
        self.save_button = QPushButton(self)
        self.save_button.setIcon(QIcon("./icon/save.png"))
        self.save_button.setShortcut('Ctrl+S')
        self.save_button.setFixedHeight(32)
        self.save_button.setFixedWidth(32)
        self.save_button.setToolTip("Save Image")
        self.save_button.clicked.connect(self.save_image)


        # set save_as button
        self.save_as_button = QPushButton(self)
        self.save_as_button.setIcon(QIcon("./icon/save_as.png"))
        self.save_as_button.setShortcut('Ctrl+S')
        self.save_as_button.setFixedHeight(32)
        self.save_as_button.setFixedWidth(32)
        self.save_as_button.setToolTip("Save As Image")
        self.save_as_button.clicked.connect(self.save_as_image)

        # set close button
        self.close_button = QPushButton(self)
        self.close_button.setIcon(QIcon("./icon/close.png"))
        self.close_button.setShortcut('Ctrl+E')
        self.close_button.setFixedHeight(32)
        self.close_button.setFixedWidth(32)
        self.close_button.setToolTip("Close Image")
        self.close_button.clicked.connect(self.close_image)

        # set draw rectangle button
        self.label_button = QPushButton(self)
        self.label_button.setIcon(QIcon("./icon/mark.png"))
        self.label_button.setShortcut('Ctrl+R')
        self.label_button.setFixedHeight(32)
        self.label_button.setFixedWidth(32)
        self.label_button.setToolTip("Draw Label")
        self.label_button.clicked.connect(self.draw_mark)

        # set hide mark button
        self.hide_mark_button = QPushButton(self)
        self.hide_mark_button.setIcon(QIcon("./icon/hide.png"))
        self.hide_mark_button.setShortcut('Ctrl+R')
        self.hide_mark_button.setFixedHeight(32)
        self.hide_mark_button.setFixedWidth(32)
        self.hide_mark_button.setToolTip("Hide Label")
        self.hide_mark_button.clicked.connect(self.hide_mark)

        # set up button
        self.up_button = QPushButton(self)
        self.up_button.setIcon(QIcon("./icon/up.png"))
        self.up_button.setShortcut('Ctrl+U')
        self.up_button.setFixedHeight(control_button_height)
        self.up_button.setFixedWidth(control_button_width)
        self.up_button.setToolTip("Up Camera")
        self.up_button.pressed.connect(self.up_pressed)
        self.up_button.released.connect(self.up_released)

        # set down button
        self.down_button = QPushButton(self)
        self.down_button.setIcon(QIcon("./icon/down.png"))
        self.down_button.setShortcut('Ctrl+D')
        self.down_button.setFixedHeight(control_button_height)
        self.down_button.setFixedWidth(control_button_width)
        self.down_button.setToolTip("Down Camera")
        self.down_button.pressed.connect(self.down_pressed)
        self.down_button.released.connect(self.down_released)
        self.image_name = ''

        # set left button
        self.left_button = QPushButton(self)
        self.left_button.setIcon(QIcon("./icon/left.png"))
        self.left_button.setShortcut('Ctrl+L')
        self.left_button.setFixedHeight(control_button_height)
        self.left_button.setFixedWidth(control_button_width)
        self.left_button.setToolTip("Ledt Camera")
        self.left_button.pressed.connect(self.left_pressed)
        self.left_button.released.connect(self.left_released)

        # set right button
        self.right_button = QPushButton(self)
        self.right_button.setIcon(QIcon("./icon/right.png"))
        self.right_button.setShortcut('Ctrl+R')
        self.right_button.setFixedHeight(control_button_height)
        self.right_button.setFixedWidth(control_button_width)
        self.right_button.setToolTip("Right Camera")
        self.right_button.pressed.connect(self.right_pressed)
        self.right_button.released.connect(self.right_released)

        # set focus near button
        self.focus_near_button = QPushButton(self)
        self.focus_near_button.setIcon(QIcon("./icon/focus_near.png"))
        self.focus_near_button.setShortcut('Ctrl+N')
        self.focus_near_button.setFixedHeight(control_button_height)
        self.focus_near_button.setFixedWidth(control_button_width)
        self.focus_near_button.setToolTip("Focus Near Image")
        self.focus_near_button.pressed.connect(self.focus_near_pressed)
        self.focus_near_button.released.connect(self.focus_near_released)

        # set focus far button
        self.focus_far_button = QPushButton(self)
        self.focus_far_button.setIcon(QIcon("./icon/focus_far.png"))
        self.focus_far_button.setShortcut('Ctrl+F')
        self.focus_far_button.setFixedHeight(control_button_height)
        self.focus_far_button.setFixedWidth(control_button_width)
        self.focus_far_button.setToolTip("Focus Far Image")
        self.focus_far_button.pressed.connect(self.focus_far_pressed)
        self.focus_far_button.released.connect(self.focus_far_released)

        # set zoom in button
        self.zoom_in_button = QPushButton(self)
        self.zoom_in_button.setIcon(QIcon("./icon/zoom_in.png"))
        self.zoom_in_button.setShortcut('Ctrl+Z+I')
        self.zoom_in_button.setFixedHeight(control_button_height)
        self.zoom_in_button.setFixedWidth(control_button_width)
        self.zoom_in_button.setToolTip("Zoom In Image")
        self.zoom_in_button.pressed.connect(self.zoom_in_pressed)
        self.zoom_in_button.released.connect(self.zoom_in_released)

        # set zoom out button
        self.zoom_out_button = QPushButton(self)
        self.zoom_out_button.setIcon(QIcon("./icon/zoom_out.png"))
        self.zoom_out_button.setShortcut('Ctrl+Z+O')
        self.zoom_out_button.setFixedHeight(control_button_height)
        self.zoom_out_button.setFixedWidth(control_button_width)
        self.zoom_out_button.setToolTip("Zoom Out Image")
        self.zoom_out_button.pressed.connect(self.zoom_out_pressed)
        self.zoom_out_button.released.connect(self.zoom_out_released)

        #thumbnail QLabel
        self.thumbnail_label = myLabel()
        self.thumbnail_label.clicked.connect(self.thumnail_clicked)

        self.video_panel = QLabel()
        self.video_panel.setFixedWidth(400)
        self.video_panel.setFixedHeight(400)
        self.video_panel.setScaledContents(True)
        # set zoom ratio
        self.zoom_ratio = 1

        self.h_layout_tool_bar = QHBoxLayout()
        self.h_layout_tool_bar.addWidget(self.exit_button)
        self.h_layout_tool_bar.addWidget(self.open_button)
        self.h_layout_tool_bar.addWidget(self.save_button)
        self.h_layout_tool_bar.addWidget(self.save_as_button)
        self.h_layout_tool_bar.addWidget(self.close_button)
        self.h_layout_tool_bar.addWidget(self.label_button)
        self.h_layout_tool_bar.addWidget(self.hide_mark_button)
        self.tool_bar = QWidget()
        self.tool_bar.setLayout(self.h_layout_tool_bar)
        self.tool_bar.setFixedHeight(50)

        self.h_layout_thumbnail = QHBoxLayout()
        self.h_layout_thumbnail.addWidget(self.thumbnail_label)
        self.thumbnail = QWidget()
        self.thumbnail.setLayout(self.h_layout_thumbnail)
        # global thumbnail_label_height
        # global thumbnail_label_width
        # self.thumbnail.setFixedHeight(thumbnail_label_height)
        # self.thumbnail.setFixedWidth(thumbnail_label_width)

        self.picture = ''
        self.original_picture = ''
        self.thumbnail_picture=''
        self.pixel_map = QPixmap()
        self.image_panel = ImageLabel()
        self.image_panel.setScaledContents(True)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_panel)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.input_mark = QLineEdit()
        self.input_mark.setFixedHeight(30)
        self.input_mark.setAlignment(Qt.AlignCenter)

        self.h_layout_left_area = QVBoxLayout()
        self.h_layout_left_area.addWidget(self.tool_bar)
        self.h_layout_left_area.addWidget(self.scroll_area)
        self.h_layout_left_area.addWidget(self.input_mark)
        self.left_area = QWidget()
        self.left_area.setLayout(self.h_layout_left_area)

        self.h_layout_control_1 = QHBoxLayout()
        self.h_layout_control_1.addWidget(self.up_button)
        self.h_layout_control_1.addWidget(self.down_button)
        self.h_layout_control_1.addWidget(self.focus_near_button)
        self.h_layout_control_1.addWidget(self.focus_far_button)
        self.control_1 = QWidget()
        self.control_1.setLayout(self.h_layout_control_1)

        self.h_layout_control_2 = QHBoxLayout()
        self.h_layout_control_2.addWidget(self.left_button)
        self.h_layout_control_2.addWidget(self.right_button)
        self.h_layout_control_2.addWidget(self.zoom_in_button)
        self.h_layout_control_2.addWidget(self.zoom_out_button)
        self.control_2 = QWidget()
        self.control_2.setLayout(self.h_layout_control_2)

        self.h_layout_control_pannel = QVBoxLayout()
        self.h_layout_control_pannel.addWidget(self.control_1)
        self.h_layout_control_pannel.addWidget(self.control_2)
        self.h_layout_control_pannel.setAlignment(Qt.AlignCenter)
        self.control_pannel = QWidget()
        self.control_pannel.setLayout(self.h_layout_control_pannel)

        self.h_layout_video_frame = QHBoxLayout()
        self.h_layout_video_frame.addWidget(self.video_panel)
        self.h_layout_video_frame.setAlignment(Qt.AlignCenter)
        self.video_frame = QWidget()
        self.video_frame.setLayout(self.h_layout_video_frame)

        self.h_layout_right_area = QVBoxLayout()
        self.h_layout_right_area.addWidget(self.video_frame)
        self.h_layout_right_area.addWidget(self.control_pannel)
        self.right_area = QWidget()
        self.right_area.setLayout(self.h_layout_right_area)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.left_area)
        self.h_layout.addWidget(self.right_area)
        self.top_area = QWidget()
        self.top_area.setLayout(self.h_layout)

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.top_area)
        self.v_layout.addWidget(self.thumbnail)
        self.setLayout(self.v_layout)

        self.setMouseTracking(False)
        self.setWindowIcon(QIcon('./icons/icon.png'))
        self.img_path = "result.jpg"

        self.mythread = VideoThread()
        self.mythread.signal.connect(self.show_video)

    def open_image(self, img_path, pkl_file_path):

        global all_point
        global all_mark_text
        global all_start_list
        print(len(all_point))
        if os.path.exists(pkl_file_path):
            pkl_file = open(pkl_file_path, 'rb')
            save_data = pickle.load(pkl_file)
            all_point = save_data[0]
            all_mark_text = save_data[1]
            all_start_list = save_data[2]
        else:
            all_point = []
            all_mark_text = []
            all_start_list = []

        self.picture = cv2.imread(img_path)
        self.original_picture = self.picture.copy()
        self.load_image(img_path)
        self.show_thumbnail_picture()

    def load_image(self, img_path):
        self.pixel_map.load(img_path)
        print("ok")
        global original_img_height, original_img_width
        original_img_width = self.pixel_map.width()
        original_img_height = self.pixel_map.height()
        self.image_panel.resize(self.pixel_map.width(), self.pixel_map.height())
        self.image_panel.setPixmap(self.pixel_map)
        self.image_panel.setAlignment(Qt.AlignCenter)
        self.thumbnail_picture = self.picture.copy()
        self.thumbnail_picture = cv2.cvtColor(self.thumbnail_picture, cv2.COLOR_BGR2RGB)
        self.thumbnail_picture = cv2.resize(self.thumbnail_picture, (thumbnail_label_width, thumbnail_label_height))
        q_image = QImage(self.thumbnail_picture[:], thumbnail_label_width, thumbnail_label_height, thumbnail_label_width * 3,
                         QImage.Format_RGB888)
        self.thumbnail_label.setPixmap(QPixmap(q_image))
        self.load_change()

    def show_video(self):
        global buffer
        self.video_panel.setPixmap(QPixmap(buffer))

    def save_image(self):
        global hide_mark_state
        if hide_mark_state == 1:
            self.hide_mark()
        global all_point
        global all_mark_text
        global all_start_list
        self.save_change()
        save_data = []
        save_data.append(all_point)
        save_data.append(all_mark_text)
        save_data.append(all_start_list)
        output_path = self.img_path.split(".")[0] + ".pkl"
        output = open(output_path, 'wb')
        pickle.dump(save_data, output)


    def save_change(self):
        self.pixel_map.save(self.img_path)
        global tmp_point
        if len(tmp_point):
            for i in range(0, len(tmp_point)):
                if (i+1) != len(tmp_point):
                    if tmp_point[i][0] == -1 or tmp_point[i+1][0] == -1:
                        continue
                    else:
                        cv2.line(self.picture, (tmp_point[i][0]+all_start, tmp_point[i][1]), (tmp_point[i+1][0]+all_start, tmp_point[i+1][1]), (0, 0, 255), 4)


        global tmp_mark_text
        if len(tmp_mark_text):
            for l in range(0, len(tmp_mark_text)):
                font = cv2.FONT_HERSHEY_COMPLEX
                cv2.putText(self.picture, tmp_mark_text[l][2], (tmp_mark_text[l][0]+all_start, tmp_mark_text[l][1]), font, 1, (0, 255, 255), 2)


        self.thumbnail_picture = self.picture.copy()
        self.thumbnail_picture = cv2.cvtColor(self.thumbnail_picture, cv2.COLOR_BGR2RGB)
        self.thumbnail_picture = cv2.resize(self.thumbnail_picture, (thumbnail_label_width, thumbnail_label_height))
        q_image = QImage(self.thumbnail_picture[:], thumbnail_label_width, thumbnail_label_height, thumbnail_label_width * 3,
                         QImage.Format_RGB888)
        self.thumbnail_label.setPixmap(QPixmap(q_image))
        global all_point
        global all_mark_text
        if len(tmp_point) != 0:
            all_point.append(copy.deepcopy(tmp_point))
            all_start_list.append(all_start)
            print(all_point)
            print(all_start_list)
        if len(tmp_mark_text) != 0:
            all_mark_text.append(copy.deepcopy(tmp_mark_text))
        tmp_point.clear()
        tmp_mark_text.clear()

    def load_change(self):
        global all_point
        global all_start_list
        global all_start
        for k in range(len(all_point)):
            point = all_point[k]
            all_start = all_start_list[k]
            if len(point):
                for i in range(0, len(point)):
                    if (i + 1) != len(point):
                        if point[i][0] == -1 or point[i + 1][0] == -1:
                            continue
                        else:
                            cv2.line(self.picture, (point[i][0] + all_start, point[i][1]),
                                     (point[i + 1][0] + all_start, point[i + 1][1]), (0, 0, 255), 4)


        global all_mark_text
        for k in range(len(all_mark_text)):
            mark_text = all_mark_text[k]
            all_start = all_start_list[k]
            if len(mark_text):
                for l in range(0, len(mark_text)):
                    font = cv2.FONT_HERSHEY_COMPLEX
                    cv2.putText(self.picture, mark_text[l][2],
                                (mark_text[l][0] + all_start, mark_text[l][1]), font, 1, (0, 255, 255), 2)

            self.thumbnail_picture = self.picture.copy()
            self.thumbnail_picture = cv2.cvtColor(self.thumbnail_picture, cv2.COLOR_BGR2RGB)
            self.thumbnail_picture = cv2.resize(self.thumbnail_picture, (thumbnail_label_width, thumbnail_label_height))
            q_image = QImage(self.thumbnail_picture[:], thumbnail_label_width, thumbnail_label_height, thumbnail_label_width * 3,
                             QImage.Format_RGB888)
            self.thumbnail_label.setPixmap(QPixmap(q_image))
        self.image_panel.update()



    def save_as_image(self):
        global hide_mark_state
        if hide_mark_state == 1:
            self.hide_mark()
        global all_point
        global all_mark_text
        self.save_change()
        save_data = []
        save_data.append(all_point)
        save_data.append(all_mark_text)
        save_as_image_name = QFileDialog.getSaveFileName(self, 'Save AS File', '/', 'jpg(*.jpg)')
        output_path = save_as_image_name[0].split(".")[0] + ".pkl"
        output = open(output_path, 'wb')
        pickle.dump(all_point, output)

    def close_image(self):
        self.image_panel.clear()
        global point
        point = []
        global mark_text
        mark_text = []

    def draw_mark(self):
        global tmp_point
        mark_x = tmp_point[len(tmp_point)-1][0]
        mark_y = tmp_point[len(tmp_point)-1][1]
        global tmp_mark_text
        tmp_mark_text.append([mark_x, mark_y, self.input_mark.text()])
        tmp_point.append([-1, -1])
        self.image_panel.update()

    def thumnail_clicked(self):
        self.save_change()
        self.show_thumbnail_picture()

    def show_thumbnail_picture(self):
        global thumbnail_x
        x = self.thumbnail_to_orignal(thumbnail_x)
        img = self.picture.copy()
        start = int(max(x-rect_width/2, 0))
        end = int(min(x+rect_width/2, img.shape[1]))
        if start == 0:
            end = rect_width + 1
        if end == img.shape[1]:
            start = img.shape[1] - rect_width - 1

        global all_start
        all_start = start
        global all_end
        all_end = end

        img = cv2.cvtColor(self.picture, cv2.COLOR_BGR2RGB)[:, start:end].copy()
        print("11111")
        q_image = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                         QImage.Format_RGB888)
        q_pixmap = QPixmap(q_image)
        self.image_panel.resize(q_pixmap.width(), q_pixmap.height())
        self.image_panel.setPixmap(q_pixmap)
        self.image_panel.setAlignment(Qt.AlignCenter)
        self.draw_rect()

    def thumbnail_to_orignal(self, x):
        x = int(x / thumbnail_label_width * original_img_width)
        return x

    def draw_rect(self):
        semi_w = int(rect_width/ 2 /original_img_width * thumbnail_label_width )
        global thumbnail_x
        x = thumbnail_x
        start = max(x - semi_w, 0)
        end = min(x + semi_w, thumbnail_label_width)
        if start == 0:
            end = 2 * semi_w + 1
        if end == thumbnail_label_width:
            start = thumbnail_label_width - semi_w*2 - 1
        img = self.thumbnail_picture.copy()
        img = cv2.rectangle(img, (start, 0), (end, thumbnail_label_height), (0, 255, 0), 2)
        q_image = QImage(img[:], thumbnail_label_width, thumbnail_label_height, thumbnail_label_width * 3,
                         QImage.Format_RGB888)
        self.thumbnail_label.setPixmap(QPixmap(q_image))

    def hide_mark(self):
        global hide_mark_state
        global all_point
        global all_mark_text
        global tmp_all_point
        global tmp_all_mark_text
        global tmp_point
        global tmp_mark_text
        global tmp_tmp_point
        global tmp_tmp_mark_text
        if hide_mark_state == 0:
            tmp_tmp_point = copy.deepcopy(tmp_point)
            tmp_tmp_mark_text = copy.deepcopy(tmp_mark_text)
            tmp_all_point = copy.deepcopy(all_point)
            tmp_all_mark_text = copy.deepcopy(all_mark_text)
            tmp_point.clear()
            tmp_mark_text.clear()
            all_point.clear()
            all_mark_text.clear()
            self.picture = self.original_picture.copy()
            hide_mark_state = 1
            self.load_image(self.img_path)
            self.show_thumbnail_picture()
        else:
            tmp_point = copy.deepcopy(tmp_tmp_point)
            tmp_mark_text = copy.deepcopy(tmp_tmp_mark_text)
            all_point = copy.deepcopy(tmp_all_point)
            all_mark_text = copy.deepcopy(tmp_all_mark_text)
            hide_mark_state = 0
            self.load_image(self.img_path)
            self.show_thumbnail_picture()
        self.image_panel.update()

    def show_window(self):
        pkl_file_path = self.img_path.split(".")[0] + ".pkl"
        self.open_image(self.img_path, pkl_file_path)
        self.mythread.start()
        self.show()

    def up_pressed(self):
        up_rotate_start(id, dll)

    def up_released(self):
        up_rotate_stop(id, dll)

    def down_pressed(self):
        down_rotate_start(id, dll)

    def down_released(self):
        down_rotate_stop(id, dll)

    def left_pressed(self):
        left_rotate_start(id, dll)

    def left_released(self):
        left_rotate_stop(id, dll)

    def right_pressed(self):
        right_rotate_start(id, dll)

    def right_released(self):
        right_rotate_stop(id, dll)

    def focus_near_pressed(self):
        focus_near_start(id, dll)

    def focus_near_released(self):
        focus_near_stop(id, dll)

    def focus_far_pressed(self):
        focus_far_start(id, dll)

    def focus_far_released(self):
        focus_far_stop(id, dll)

    def zoom_in_pressed(self):
        zoom_in_start(id, dll)

    def zoom_in_released(self):
        zoom_in_stop(id, dll)

    def zoom_out_pressed(self):
        zoom_out_start(id, dll)

    def zoom_out_released(self):
        zoom_out_stop(id, dll)


#if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app.setApplicationName("Image Mask")
#     window = MarkWindow()
#     sys.exit(app.exec_())