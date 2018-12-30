import sys
from camera_function import *
from function import *
from mark_UI import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from window_size import *

window_width, window_height = get_window_size()
toolbar_height = 200
camera_label_width = window_width - 100
camera_label_height = window_height - toolbar_height
button_width = 32
button_height = 32

mutex = threading.Lock()

id, dll = init()
buffer = ''
col_start = 0
col_end = 0
row_start = 0
row_end = 0
start_point = [0, 0]
end_point = [0, 0]
draw_flag = 0
draw_step = 0
draw_type = 0
set_flag = 0
warning_state = 0
line = [0, 0, 0]
move_flag = 0


def get_id_and_dll():
    global id
    global dll
    return id, dll


class cameraLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        global set_flag
        global draw_flag
        global line
        if set_flag == 0:
            return
        global_point = event.globalPos()
        local_point = self.mapFromGlobal(global_point)
        global start_point
        global end_point
        global draw_step
        if draw_step == 0:
            start_point = [local_point.x(), local_point.y()]
            draw_step = 1
            print(start_point)
        else:
            end_point = [local_point.x(), local_point.y()]
            line[0] = end_point[1] - start_point[1]
            line[1] = start_point[0] - end_point[0]
            line[2] = end_point[0]*start_point[1] - start_point[0]*end_point[1]
            draw_step = 0
            set_flag = 0
            draw_flag = 1
            print(end_point)
            print(line)


class VideoThread(QThread):

    signal = pyqtSignal()

    def __init__(self):
        super(VideoThread, self).__init__()

    def run(self):
        cap = cv2.VideoCapture('rtsp://iot02:iot2015128@192.168.134.122:554//Streaming/Channels/1')
        #cap = cv2.VideoCapture(0)

        if cap.isOpened():
            rval, frame = cap.read()
            while not rval:
                rval, frame = cap.read()
            print('ture')
        else:
            rval = False
            print('False')
        # 循环使用cv2的read()方法读取视频帧
        video_background = cv2.createBackgroundSubtractorMOG2()

        while rval:
            global draw_type
            global start_point
            global end_point
            global warning_state
            global move_flag
            rval, frame1 = cap.read()
            while not rval:
                rval, frame1 = cap.read()
            rval, frame2 = cap.read()
            while not rval:
                rval, frame2 = cap.read()
            frame1 = cv2.resize(frame1, (camera_label_width, camera_label_height))
            frame2 = cv2.resize(frame2, (camera_label_width, camera_label_height))

            screen_move_detect(frame2, video_background, move_flag)

            frame = frame2.copy()

            if draw_flag != 0:
                start = (start_point[0], start_point[1])
                end = (end_point[0], end_point[1])
                row_start = min(start_point[1], end_point[1])
                row_end = max(start_point[1], end_point[1])+1
                col_start = min(start_point[0], end_point[0])
                col_end = max(start_point[0], end_point[0])+1

                if draw_type == 0:
                    frame1_s = frame1[row_start:row_end, col_start:col_end]
                    frame2_s = frame2[row_start:row_end, col_start:col_end]
                    warning_state = move_detect(frame1_s, frame2_s)
                    frame = cv2.rectangle(frame, start, end, (0, 255, 0), 2)
                else:
                    global line
                    thresh = 200
                    frame1 = cv2.resize(frame1, (camera_label_width, camera_label_height))
                    frame = frame1.copy()
                    if row_end - row_start < thresh:
                        row_start = max(0, row_start - thresh)
                        row_end = min(camera_label_height+1, row_end + thresh)
                    if col_end -col_start < thresh:
                        col_start = max(0, col_start - thresh)
                        col_end = min(camera_label_width+1, col_end + thresh)
                    print(col_start, row_start)
                    print(col_end, row_end)
                    frame1_s = frame1[row_start:row_end, col_start:col_end]
                    frame2_s = frame2[row_start:row_end, col_start:col_end]
                    warning_state = line_detect(frame1_s, frame2_s, row_start, col_start, line)
                    frame = cv2.line(frame, start, end, (0, 255, 0), 2)
            else:
                warning_state = 0
            show_image = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2RGB)
            video_image = QImage(show_image.data, show_image.shape[1], show_image.shape[0], QImage.Format_RGB888)
            global buffer
            buffer = video_image
            self.signal.emit()
        cap.release()
        cv2.destroyAllWindows()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        # set up button
        self.up_button = QPushButton(self)
        self.up_button.setIcon(QIcon("./icon/up.png"))
        self.up_button.setShortcut('Ctrl+U')
        self.up_button.setFixedHeight(button_height)
        self.up_button.setFixedWidth(button_width)
        self.up_button.setToolTip("Up Camera")
        self.up_button.pressed.connect(self.up_pressed)
        self.up_button.released.connect(self.up_released)

        # set down button
        self.down_button = QPushButton(self)
        self.down_button.setIcon(QIcon("./icon/down.png"))
        self.down_button.setShortcut('Ctrl+D')
        self.down_button.setFixedHeight(button_height)
        self.down_button.setFixedWidth(button_width)
        self.down_button.setToolTip("Down Camera")
        self.down_button.pressed.connect(self.down_pressed)
        self.down_button.released.connect(self.down_released)
        self.image_name = ''

        # set left button
        self.left_button = QPushButton(self)
        self.left_button.setIcon(QIcon("./icon/left.png"))
        self.left_button.setShortcut('Ctrl+L')
        self.left_button.setFixedHeight(button_height)
        self.left_button.setFixedWidth(button_width)
        self.left_button.setToolTip("Ledt Camera")
        self.left_button.pressed.connect(self.left_pressed)
        self.left_button.released.connect(self.left_released)

        # set right button
        self.right_button = QPushButton(self)
        self.right_button.setIcon(QIcon("./icon/right.png"))
        self.right_button.setShortcut('Ctrl+R')
        self.right_button.setFixedHeight(button_height)
        self.right_button.setFixedWidth(button_width)
        self.right_button.setToolTip("Right Camera")
        self.right_button.pressed.connect(self.right_pressed)
        self.right_button.released.connect(self.right_released)


        # set focus near button
        self.focus_near_button = QPushButton(self)
        self.focus_near_button.setIcon(QIcon("./icon/focus_near.png"))
        self.focus_near_button.setShortcut('Ctrl+N')
        self.focus_near_button.setFixedHeight(button_height)
        self.focus_near_button.setFixedWidth(button_width)
        self.focus_near_button.setToolTip("Focus Near Image")
        self.focus_near_button.pressed.connect(self.focus_near_pressed)
        self.focus_near_button.released.connect(self.focus_near_released)

        # set focus far button
        self.focus_far_button = QPushButton(self)
        self.focus_far_button.setIcon(QIcon("./icon/focus_far.png"))
        self.focus_far_button.setShortcut('Ctrl+F')
        self.focus_far_button.setFixedHeight(button_height)
        self.focus_far_button.setFixedWidth(button_width)
        self.focus_far_button.setToolTip("Focus Far Image")
        self.focus_far_button.pressed.connect(self.focus_far_pressed)
        self.focus_far_button.released.connect(self.focus_far_released)

        # set zoom in button
        self.zoom_in_button = QPushButton(self)
        self.zoom_in_button.setIcon(QIcon("./icon/zoom_in.png"))
        self.zoom_in_button.setShortcut('Ctrl+Z+I')
        self.zoom_in_button.setFixedHeight(button_height)
        self.zoom_in_button.setFixedWidth(button_width)
        self.zoom_in_button.setToolTip("Zoom In Image")
        self.zoom_in_button.pressed.connect(self.zoom_in_pressed)
        self.zoom_in_button.released.connect(self.zoom_in_released)

        # set zoom out button
        self.zoom_out_button = QPushButton(self)
        self.zoom_out_button.setIcon(QIcon("./icon/zoom_out.png"))
        self.zoom_out_button.setShortcut('Ctrl+Z+O')
        self.zoom_out_button.setFixedHeight(button_height)
        self.zoom_out_button.setFixedWidth(button_width)
        self.zoom_out_button.setToolTip("Zoom Out Image")
        self.zoom_out_button.pressed.connect(self.zoom_out_pressed)
        self.zoom_out_button.released.connect(self.zoom_out_released)

        # set Left splicing
        self.left_splic_button = QPushButton(self)
        self.left_splic_button.setIcon(QIcon("./icon/left_splic.png"))
        self.left_splic_button.setShortcut('Ctrl+L+S')
        self.left_splic_button.setFixedHeight(button_height)
        self.left_splic_button.setFixedWidth(button_width)
        self.left_splic_button.setToolTip("Left Splicing Image")
        self.left_splic_button.clicked.connect(self.left_splic_clicked)

        # set Right splicing
        self.right_splic_button = QPushButton(self)
        self.right_splic_button.setIcon(QIcon("./icon/right_splic.png"))
        self.right_splic_button.setShortcut('Ctrl+R+S')
        self.right_splic_button.setFixedHeight(button_height)
        self.right_splic_button.setFixedWidth(button_width)
        self.right_splic_button.setToolTip("Right Splicing Image")
        self.right_splic_button.clicked.connect(self.right_splic_clicked)

        # set splicing_stop
        self.splic_stop_button = QPushButton(self)
        self.splic_stop_button.setIcon(QIcon("./icon/stop.png"))
        self.splic_stop_button.setShortcut('Ctrl+R+S')
        self.splic_stop_button.setFixedHeight(button_height)
        self.splic_stop_button.setFixedWidth(button_width)
        self.splic_stop_button.setToolTip("Right Splicing Image")
        self.splic_stop_button.clicked.connect(self.splic_stop)

        # set draw_waring_rect
        self.draw_rect_button = QPushButton(self)
        self.draw_rect_button.setIcon(QIcon("./icon/rect.png"))
        self.draw_rect_button.setShortcut('Ctrl+R+S')
        self.draw_rect_button.setFixedHeight(button_height)
        self.draw_rect_button.setFixedWidth(button_width)
        self.draw_rect_button.setToolTip("Draw Warning Rect")
        self.draw_rect_button.clicked.connect(self.set_rect)

        # set draw_waring_line
        self.draw_line_button = QPushButton(self)
        self.draw_line_button.setIcon(QIcon("./icon/line.png"))
        self.draw_line_button.setShortcut('Ctrl+R+S')
        self.draw_line_button.setFixedHeight(button_height)
        self.draw_line_button.setFixedWidth(button_width)
        self.draw_line_button.setToolTip("Draw Warning Line")
        self.draw_line_button.clicked.connect(self.set_line)

        # set mark
        self.mark_button = QPushButton(self)
        self.mark_button .setIcon(QIcon("./icon/change.png"))
        self.mark_button .setShortcut('Ctrl+C')
        self.mark_button .setFixedHeight(button_height)
        self.mark_button.setFixedWidth(button_width)
        self.mark_button .setToolTip("Mark Image")

        # move detect
        self.move_button = QPushButton(self)
        self.move_button.setIcon(QIcon("./icon/move.png"))
        self.move_button.setShortcut('Ctrl+M')
        self.move_button.setFixedHeight(button_height)
        self.move_button.setFixedWidth(button_width)
        self.move_button.setToolTip("Move Detect")
        self.move_button.clicked.connect(self.move_mark)

        self.image_panel = cameraLabel()
        self.image_panel.setFixedWidth(camera_label_width)
        self.image_panel.setFixedHeight(camera_label_height)
        self.image_panel.setScaledContents(True)

        self.warning_image_panel = cameraLabel()
        self.warning_image_panel.setFixedWidth(button_height)
        self.warning_image_panel.setFixedHeight(button_width)
        self.warning_image_panel.setScaledContents(True)
        self.red = cv2.imread("icon/red.png")
        self.green = cv2.imread("icon/green.png")

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.up_button)
        self.h_layout.addWidget(self.down_button)
        self.h_layout.addWidget(self.left_button)
        self.h_layout.addWidget(self.right_button)
        self.h_layout.addWidget(self.focus_near_button)
        self.h_layout.addWidget(self.focus_far_button)
        self.h_layout.addWidget(self.zoom_in_button)
        self.h_layout.addWidget(self.zoom_out_button)
        self.h_layout.addWidget(self.right_splic_button)
        self.h_layout.addWidget(self.left_splic_button)
        self.h_layout.addWidget(self.splic_stop_button)
        self.h_layout.addWidget(self.mark_button)
        self.h_layout.addWidget(self.move_button)
        self.h_layout.addWidget(self.draw_rect_button)
        self.h_layout.addWidget(self.draw_line_button)
        self.h_layout.addWidget(self.warning_image_panel)
        self.tool_bar = QWidget()
        self.tool_bar.setLayout(self.h_layout)
        self.tool_bar.setFixedHeight(48)

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.tool_bar)
        self.v_layout.addWidget(self.image_panel)
        self.setLayout(self.v_layout)
        self.setGeometry(150, 100, window_width, window_height)
        self.show()

        self.show_waring_state()
        self.mythread = VideoThread()
        self.mythread.signal.connect(self.show_video)
        self.mythread.signal.connect(self.show_waring_state)
        self.mythread.start()

    def move_mark(self):
        global move_flag
        move_flag = move_flag ^ 1

    def show_video(self):
        global buffer
        self.image_panel.setPixmap(QPixmap(buffer))

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

    def right_splic_clicked(self):
        right_splic_thread = threading.Thread(target=splicing, args=(id, dll, 1))
        mutex.acquire()
        set_start(True)
        mutex.release()
        right_splic_thread.start()

    def left_splic_clicked(self):
        left_splic_thread = threading.Thread(target=splicing, args=(id, dll, 0))
        mutex.acquire()
        set_start(True)
        mutex.release()
        left_splic_thread.start()

    def splic_stop(self):
        mutex.acquire()
        set_start(False)
        print("Splic stoped!")
        mutex.release()

    def set_rect(self):
        global draw_type
        global set_flag
        global draw_flag
        draw_flag = 0
        draw_type = 0
        set_flag = 1

    def set_line(self):
        global draw_type
        global set_flag
        global draw_flag
        draw_flag = 0
        draw_type = 1
        set_flag = 1

    def show_waring_state(self):
        global warning_state
        if warning_state == 1:
            show_image = cv2.cvtColor(self.red, cv2.COLOR_BGR2RGB)
        else:
            show_image = cv2.cvtColor(self.green, cv2.COLOR_BGR2RGB)
        warning_image = QImage(show_image, show_image.shape[1], show_image.shape[0], QImage.Format_RGB888)
        self.warning_image_panel.setPixmap(QPixmap(warning_image))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Image Mask")
    mark_window = MarkWindow()
    window = MainWindow()
    window.mark_button.clicked.connect(mark_window.show_window)
    sys.exit(app.exec_())

