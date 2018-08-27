"ocr相关，dpi识别，截图等"
from os import getcwd
from ctypes import windll
from win32gui import FindWindow, SetWindowPos, GetWindowRect
from win32con import HWND_TOPMOST, HWND_TOP, SWP_DEFERERASE, SWP_NOREPOSITION

from PIL import ImageGrab
from tesserocr import image_to_text

class ocrError(Exception):
    pass

class yysWindow:

    def __init__(self):
        self.handle = 0
        self.set_dpi()
        self.get_yys_handle()


    def set_dpi(self):
        "设置系统的缩放信息dpi"
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    def get_yys_handle(self):
        "获取阴阳师的窗口句柄"
        self.handle = FindWindow(None, "阴阳师-网易游戏")
        if not self.handle:
            raise ocrError("cannot find yys window")
        return self.handle

    def adjust_yys_resolution(self):
        "调节阴阳师的分辨率，置顶"
        SetWindowPos(self.handle, HWND_TOPMOST, 0, 0, 1533, 901, SWP_DEFERERASE|SWP_NOREPOSITION)
    
    def release_yys_topmost(self):
        x, y, _, _ = self.get_window_rect()
        SetWindowPos(self.handle, HWND_TOP, x, y, 1533, 901, SWP_DEFERERASE|SWP_NOREPOSITION)

    def get_window_rect(self):
        "获取当前窗口的坐标"
        return GetWindowRect(self.handle)

    def snap_shot(self):
        "输出截图"
        # 获取yys窗口句柄
        if not self.handle:
            self.get_yys_handle()
        # 检查当前yys分辨率
        x1, _, x2, _ = self.get_window_rect()
        # 调整分辨率，如有必要
        if (x2 - x1) != 1533:
            self.adjust_yys_resolution()
        # 用PIL进行截图
        return ImageGrab.grab(bbox=self.get_window_rect())

class OCR:

    check_position = [
            ((755, 199), (255, 236, 115), 1),
            ((741, 231), (255, 240, 114), 2),
            ((755, 263), (255, 235, 112), 3),
            ((820, 263), (255, 237, 112), 4),
            ((834, 231), (255, 240, 115), 5),
            ((820, 199), (255, 237, 112), 6),
            ]
    
    check_yuhun = [
        ((845, 245), (239, 110, 25)),
        ((845, 240), (113, 82, 68)),
        ((860, 245), (228, 86, 34))
    ]

    name_rect = (828, 192, 982, 233)
    bottom_line_rgb = (177, 140, 120)
    status_rect_data = (740, 290, 1095)

    def __init__(self, img):
        self.image = img
        self.pix = img.load()
        self.path = getcwd()
        self.position = 0
        self.calculate_rect()

    def calculate_rect(self):
        if self.is_yuhun_exist():
            self.check_yuhun_position()
            bottom_y = self.get_status_bottom()
            if not bottom_y:
                raise ocrError("cannot find yuhun status bottom line")
            self.status_rect = (*self.status_rect_data, bottom_y - 3)
            self.extra_rect = (self.status_rect_data[0], bottom_y + 8, self.status_rect_data[2], bottom_y + 48)
        else:
            raise ocrError("cannot find yuhun status pic")

    
    def ocr_text(self, img):
        return image_to_text(img, lang="yys", psm=6, path=self.path)
    
    def is_yuhun_exist(self):
        for coordinate, pattern in self.check_yuhun:
            if not self.check_rgb(self.pix[coordinate], pattern):
                return False
        return True

    def check_yuhun_position(self):
        "找御魂的位置"
        for coordinate, pattern, position in self.check_position:
            if self.check_rgb(self.pix[coordinate], pattern):
                self.position = position
                return self.position
    
    def get_name_img(self):
        return self.image.crop(self.name_rect)
    
    def get_name_text(self):
        pass
    
    def get_status_img(self):
        return self.image.crop(self.status_rect)
    
    def get_status_text(self):
        raw = self.ocr_text(self.get_status_img())
        return self.parse_raw_text(raw)

    def parse_raw_text(self, raw):
        res = []
        for char in raw:
            if char == " ": continue
            if char == "中" and res[-1] != "命": char = "+"
            res.append(char)
        return "".join(res)
    
    def parse_status_data(self, string):

        def put_in(res, temp):
            if temp:
                res.append("".join(temp))
                temp.clear()
    
        name = []
        number = []
        name_temp = []
        number_temp = []
        num_pattern = "0123456789%"
        for char in string:
            if char == "\n" or char == "+":
                put_in(name, name_temp)
                put_in(number, number_temp)
            elif char in num_pattern:
                number_temp.append(char)
            else:
                name_temp.append(char)
        return name, number

    def get_extra_img(self):
        return self.image.crop(self.extra_rect)

    def get_status_bottom(self):
        # 从横坐标900，纵坐标500，垂直向上找色(176, 138, 120)
        for y in range(500, 290, -1):
            if self.check_rgb(self.pix[900, y], self.bottom_line_rgb):
                return y

    @staticmethod
    def check_rgb(sample, pattern, offset=5):
        for s, p in zip(sample, pattern):
            if abs(s - p) > offset:
                return False
        return True
    
    # @staticmethod
    # def img_init(img):
    #     pix = img.load()
    #     for x in range(img.size[0]):
    #         for y in range(img.size[1]):
    #             pix[x, y] = (255, 255, 255) if pix[x, y] == (203, 181, 156) else (0, 0, 0)

class OCR_win7(OCR):

    check_position = [
            ((756, 195), (255, 240, 115), 1),
            ((742, 228), (255, 240, 114), 2),
            ((756, 261), (255, 240, 115), 3),
            ((822, 261), (255, 240, 114), 4),
            ((836, 228), (255, 240, 115), 5),
            ((822, 195), (255, 240, 114), 6),
            ]
    
    check_yuhun = [
        ((845, 245), (237, 88, 27)),
        ((846, 238), (97, 86, 81)),
        ((860, 240), (216, 67, 61))
    ]

    name_rect = (830, 191, 973, 229)
    bottom_line_rgb = (179, 143, 124)
    status_rect_data = (738, 286, 1095)


def main():
    "测试模块"
    # from time import time
    # 获取yys句柄
    yys = yysWindow()
    hw = yys.get_yys_handle()
    print("yys的窗口句柄是", hw)
    # 截图并显示
    img = yys.snap_shot()
    # 移交ocr处理文字
    ocr = OCR(img)
    # new_img = ocr.get_status_img()
    # ocr.img_init(new_img)
    # new_img.show()
    status = ocr.get_status_text()
    print(ocr.position)
    print(status)
    # file_num = round(time())
    # ocr.get_extra_img().save("extra_"+str(file_num)+".bmp")

if __name__ == '__main__':
    main()