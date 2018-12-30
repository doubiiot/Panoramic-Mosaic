from camera_function import *


def splicing(id, dll, flag):
    imgs = capture_by_step(id, dll, flag)
    stitcher = cv2.createStitcher(False)
    status, result = stitcher.stitch(imgs)
    if status == cv2.STITCHER_OK:
        print("OK!")
        cv2.imwrite("result.jpg", result)
    else:
        print("Failed!")


def move_detect(img1, img2):

    print("Rect Detecting")
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    img1_gray = cv2.GaussianBlur(img1_gray, (21, 21), 0)
    img2_gray = cv2.GaussianBlur(img2_gray, (21, 21), 0)

    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

    diff = cv2.absdiff(img1_gray, img2_gray)
    diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]  # 二值化阈值处理
    diff = cv2.dilate(diff, es, iterations=2)  # 形态学膨胀

    image, contours, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)  # 该函数计算一幅图像中目标的轮廓
    warning_state = 0
    for c in contours:
        if cv2.contourArea(c) < 500:  # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            continue
        warning_state = 1
        break
    return warning_state


def line_detect(img1, img2, row_offset, col_offset, line):

    print("Line Detecting")
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    img1_gray = cv2.GaussianBlur(img1_gray, (21, 21), 0)
    img2_gray = cv2.GaussianBlur(img2_gray, (21, 21), 0)

    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

    diff = cv2.absdiff(img1_gray, img2_gray)
    diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]  # 二值化阈值处理
    diff = cv2.dilate(diff, es, iterations=2)  # 形态学膨胀

    image, contours, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)  # 该函数计算一幅图像中目标的轮廓
    warning_state = 0
    for c in contours:
        if cv2.contourArea(c) < 2000:  # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
            continue
        (x, y, w, h) = cv2.boundingRect(c)  # 该函数计算矩形的边界框
        x = x + col_offset
        y = y + row_offset
        p0 = [x, y]
        p1 = [x+w, y]
        p2 = [x, y+h]
        p3 = [x+w, y+h]
        print(p0)
        print(p1)
        print(p2)
        print(p3)
        if rect_is_on_line(p0, p1, p2, p3, line):
            warning_state = 1
            break
    return warning_state


def rect_is_on_line(p0, p1, p2, p3, line):
    r0 = calculate_line(p0, line)
    r1 = calculate_line(p1, line)
    r2 = calculate_line(p2, line)
    r3 = calculate_line(p3, line)

    if r0>0 and r1>0 and r2>0 and r3>0:
        return False
    elif r0<0 and r1<0 and r2<0 and r3<0:
        return False
    else:
        return True


def calculate_line(p, line):
    a = line[0]
    b = line[1]
    c = line[2]

    x = p[0]
    y = p[1]

    result = a*x + b*y + c
    return result


def screen_move_detect(img, video_background, move_flag):
    if move_flag == 1:
        background_mask = video_background.apply(img)
        image, contours, hierarchy = cv2.findContours(background_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for rectangle in contours:
            if cv2.contourArea(rectangle) > 1000:
                x, y, width, height = cv2.boundingRect(rectangle)
                cv2.rectangle(img, (x, y), (x + width, y + height), (255, 255, 0), 2)
                continue
    return img
        # img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        # img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        #
        # img1_gray = cv2.GaussianBlur(img1_gray, (21, 21), 0)
        # img2_gray = cv2.GaussianBlur(img2_gray, (21, 21), 0)
        #
        # es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        #
        # diff = cv2.absdiff(img1_gray, img2_gray)
        # diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]  # 二值化阈值处理
        # diff = cv2.dilate(diff, es, iterations=2)  # 形态学膨胀
        #
        # image, contours, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL,
        #                                               cv2.CHAIN_APPROX_SIMPLE)  # 该函数计算一幅图像中目标的轮廓
        #
        # for rectangle in contours:
        #     if cv2.contourArea(rectangle) > 2000:  # 对于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示。对于光照不变和噪声低的摄像头可不设定轮廓最小尺寸的阈值
        #         x, y, width, height = cv2.boundingRect(rectangle)
        #         cv2.rectangle(img2, (x, y), (x + width, y + height), (255, 255, 0), 2)
        #         continue

def blur_detect(img):
    blur_thresh = 200
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    degree = cv2.Laplacian(img_gray, cv2.CV_64F).var()
    if degree < blur_thresh:
        return True
    return False
