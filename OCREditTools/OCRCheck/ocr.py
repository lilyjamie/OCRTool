# -*- coding: utf-8 -*-

import os
import cv2
import time


from OCREditTools.drivers.ocr_cloud import OCRCloud
from OCREditTools.drivers.ocr_local import OCRLocal
from OCREditTools.Func import is_text_match


PATTERN = 0
LANG = 1
MAX_CHECK_COUNT = 2
IMG_FILTER = 3
NICE = 4
CONFIG = 5
TEXT_COMPARE_METHOD = 6
BORDER = 7


class OCR:
    OCR_CKP_TARGET_TEXT = 'target_text'
    OCR_CKP_X1Y1_X2Y2 = 'x1y1_x2y2'
    OCR_CKP_LANG = 'lang'
    OCR_CKP_MAX_CHECK_COUNT = 'max_check_count'
    OCR_CKP_IMG_FILTER = 'img_filter'
    OCR_CKP_NICE = 'nice'
    OCR_CKP_CONFIG = 'config'
    OCR_CKP_INHERIT = 'inherit'
    OCR_CKP_TEXT_COMPARE_METHOD = 'text_compare_method'
    OCR_CKP_IMG_BORDER = 'img_border'
    DEBUG_DIRECTORY = './debug'

    def __init__(self, pic_path="pic.jpg", ocr_engine='local', debuglevel=None):
        self.pic_path = pic_path
        self.debuglevel = debuglevel

        if str('cloud') in ocr_engine.lower():
            OCR.ocr_cloud = OCRCloud()

        self.checkpoints = dict()
        self.__ocr_debug_init()
        self.__bInit = True

    def _ocr_get_frame_text(self,
                            frame,
                            x1y1_x2y2,
                            border=None,
                            img_filter='',
                            ocr_engine='local',
                            lang='eng',
                            config=''):
        if not self.__bInit:
            return None

        pos_len = len(x1y1_x2y2)
        if pos_len < 4:
            return None
        img = frame[x1y1_x2y2[1]:x1y1_x2y2[3], x1y1_x2y2[0]:x1y1_x2y2[2]]
        self._ocr_save_debug_img(img, 'ori_cut')
        if border and len(border) == 4:
            point = img[0, 0]
            img = cv2.copyMakeBorder(img, int(border[0]), int(border[1]), int(border[2]), int(border[3]),
                                     cv2.BORDER_CONSTANT, value=[int(point[0]), int(point[1]), int(point[2])])
        if pos_len == 5:
            resize_ration = x1y1_x2y2[4]
            img = cv2.resize(img, None, fx=resize_ration, fy=resize_ration)

        if img_filter.upper() == str('GRAY'):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img_filter.upper() == str('BINARY'):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if ret:
                img = bin_img
        elif img_filter.upper() == str('BINARY-INV'):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, bin_img_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            if ret:
                img = bin_img_inv

        self.return_str = ''

        if ocr_engine.lower() == str('local'):
            self.return_str = OCRLocal.ocr_local_get_frame_text(img, lang, config)
        else:
            if hasattr(OCR, 'ocr_cloud'):
                temp_file_path = './temp.jpg'
                cv2.imwrite(temp_file_path, img)
                self.return_str = self.ocr_cloud.ocr_cloud_get_img_text(temp_file_path, lang, config)
            else:
                print('OCR Cloud not init.')

        self._ocr_save_debug_img(img, 'filter')
        print("return str:" + self.return_str)
        return self.return_str

    def ocr_release(self):
        if self.__bInit:
            self.__bInit = False
            cv2.destroyAllWindows()
            print('OCR Release')

    def ocr_get_img_text(self, img_file_path, lang='eng', config='', ocr_engine='local'):
        if not self.__bInit:
            return None

        return_str = ''

        if ocr_engine.lower() == str('local'):
            return_str = OCRLocal.ocr_local_get_img_text(img_file_path, lang, config)
        else:
            if hasattr(OCR, 'ocr_cloud'):
                return_str = self.ocr_cloud.ocr_cloud_get_img_text(img_file_path, lang, config)
            else:
                print('OCR Cloud not init.')

        print("return_str:" + return_str)
        return return_str

    def ocr_get_video_text(self, x1y1_x2y2, border=None, img_filter='', ocr_engine='local', lang='eng', config=''):
        if not self.__bInit:
            return None
        frame = cv2.imread(self.pic_path)
        text = self._ocr_get_frame_text(frame, x1y1_x2y2, border, img_filter, ocr_engine, lang, config)
        return text

    def ocr_match_video_text(self,
                             target_text,
                             max_frame_count,
                             x1y1_x2y2,
                             border=None,
                             img_filter='auto',
                             ocr_engine='local',
                             lang='eng',
                             config='',
                             nice=100,
                             text_compare_method=None):
        if not self.__bInit:
            return False, -1.0

        frame = cv2.imread(self.pic_path)

        for count in range(0, int(max_frame_count)):

            if img_filter.upper() == str('AUTO'):
                for filter_name in ['BINARY-INV', '', 'GRAY', 'BINARY']:
                    ret, ratio = is_text_match(target_text,
                                               self._ocr_get_frame_text(frame,
                                                                        x1y1_x2y2,
                                                                        border,
                                                                        filter_name,
                                                                        ocr_engine,
                                                                        lang,
                                                                        config),
                                               nice, text_compare_method)
                    if ret:
                        print(filter_name + 'Img: ' + str(count))
                        return ret, ratio
            else:
                ret, ratio = is_text_match(target_text,
                                           self._ocr_get_frame_text(frame,
                                                                    x1y1_x2y2,
                                                                    border,
                                                                    img_filter,
                                                                    ocr_engine,
                                                                    lang,
                                                                    config),
                                           nice, text_compare_method)
                if ret:
                    print(img_filter + 'Img: ' + str(count))
                    return ret, ratio
        return False, -1.0

    def ocr_load_checkpoint_config(self, config_name, config_value):
        temp_ckp = {config_name: config_value}
        self.checkpoints.update(temp_ckp)

    def ocr_clear_checkpoint(self):
        self.checkpoints.clear()

    @staticmethod
    def _ocr_checkpoint_get_xy(x1y1_x2y2_js):
        if len(x1y1_x2y2_js) > 4:
            x1y1_x2y2 = (x1y1_x2y2_js[0], x1y1_x2y2_js[1], x1y1_x2y2_js[2], x1y1_x2y2_js[3],
                         x1y1_x2y2_js[4])
        else:
            x1y1_x2y2 = (x1y1_x2y2_js[0], x1y1_x2y2_js[1], x1y1_x2y2_js[2], x1y1_x2y2_js[3])

        return x1y1_x2y2

    @staticmethod
    def _ocr_prepare_params(content, target_text):
        pattern = target_text
        lang = 'eng'
        max_check_count = 1
        img_filter = ''
        nice = 100
        config = ''
        text_compare_method = 'br2sp'
        border = None

        if OCR.OCR_CKP_TARGET_TEXT in content:
            pattern = content[OCR.OCR_CKP_TARGET_TEXT]

        if OCR.OCR_CKP_LANG in content:
            lang = content[OCR.OCR_CKP_LANG]

        if OCR.OCR_CKP_MAX_CHECK_COUNT in content:
            max_check_count = content[OCR.OCR_CKP_MAX_CHECK_COUNT]

        if OCR.OCR_CKP_IMG_FILTER in content:
            img_filter = content[OCR.OCR_CKP_IMG_FILTER]

        if OCR.OCR_CKP_NICE in content:
            nice = content[OCR.OCR_CKP_NICE]

        if OCR.OCR_CKP_CONFIG in content:
            config = content[OCR.OCR_CKP_CONFIG]

        if OCR.OCR_CKP_TEXT_COMPARE_METHOD in content:
            text_compare_method = content[OCR.OCR_CKP_TEXT_COMPARE_METHOD]

        if OCR.OCR_CKP_IMG_BORDER in content:
            border_js = content[OCR.OCR_CKP_IMG_BORDER]
            if type(border_js) == list and len(border_js) == 4:
                border = (border_js[0], border_js[1], border_js[2], border_js[3])

        return (pattern,
                lang,
                max_check_count,
                img_filter,
                nice,
                config,
                text_compare_method,
                border)

    def _ocr_checkpoint_core(self, content, target_text):
        if OCR.OCR_CKP_INHERIT in content:
            inherit_ckp = content[OCR.OCR_CKP_INHERIT]
            content = self.checkpoints[inherit_ckp]

        x1y1_x2y2 = None

        if OCR.OCR_CKP_X1Y1_X2Y2 in content:
            x1y1_x2y2_js = content[OCR.OCR_CKP_X1Y1_X2Y2]

            if type(x1y1_x2y2_js) == list and len(x1y1_x2y2_js) >= 4:
                x1y1_x2y2 = self._ocr_checkpoint_get_xy(x1y1_x2y2_js)
            else:
                print('Image size error')
                return False, -1.0

        p = self._ocr_prepare_params(content, target_text)

        return self.ocr_match_video_text(p[PATTERN],
                                         p[MAX_CHECK_COUNT],
                                         x1y1_x2y2,
                                         p[BORDER],
                                         p[IMG_FILTER],
                                         'local',
                                         p[LANG],
                                         p[CONFIG],
                                         p[NICE],
                                         p[TEXT_COMPARE_METHOD])

    def ocr_checkpoint(self, check_point_name, target_text=''):
        if not self.__bInit:
            return False, -1.0

        if check_point_name in self.checkpoints.keys():
            content = self.checkpoints[check_point_name]

            if type(content) == dict:
                return self._ocr_checkpoint_core(content, target_text)
            else:
                print('Check Point: ' + check_point_name + ' error.')
                return False, -1.0
        else:
            print('OCR Check Point: ' + check_point_name + ' is not set.')
            return False, -1.0

    def _ocr_checkpoint_get_text_core(self, content):
        if OCR.OCR_CKP_INHERIT in content:
            inherit_ckp = content[OCR.OCR_CKP_INHERIT]
            content = self.checkpoints[inherit_ckp]

        x1y1_x2y2 = None

        if OCR.OCR_CKP_X1Y1_X2Y2 in content:
            x1y1_x2y2_js = content[OCR.OCR_CKP_X1Y1_X2Y2]

            if type(x1y1_x2y2_js) == list and len(x1y1_x2y2_js) >= 4:
                x1y1_x2y2 = self._ocr_checkpoint_get_xy(x1y1_x2y2_js)
            else:
                print('Image size error')
                return ''

        p = self._ocr_prepare_params(content, '')

        return self.ocr_get_video_text(x1y1_x2y2,
                                       p[BORDER],
                                       p[IMG_FILTER],
                                       'local',
                                       p[LANG],
                                       p[CONFIG])

    def ocr_checkpoint_txt(self, check_point_name):
        if not self.__bInit:
            return ''

        if check_point_name in self.checkpoints.keys():
            content = self.checkpoints[check_point_name]

            if type(content) == dict:
                return self._ocr_checkpoint_get_text_core(content)
            else:
                print('Check Point: ' + check_point_name + ' error.')
                return ''
        else:
            print('OCR Check Point: ' + check_point_name + ' is not set.')
            return ''

    def _ocr_save_debug_img(self, img, name):
        if self.debuglevel and (str('Debug') == str(self.debuglevel)):
            temp_str = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            cv2.imwrite(OCR.DEBUG_DIRECTORY + '/' + name + str('_') + temp_str + str('.jpeg'), img)

    def __ocr_debug_init(self):
        if self.debuglevel and (str('Debug') == str(self.debuglevel)):
            if not os.path.exists(OCR.DEBUG_DIRECTORY):
                os.makedirs(OCR.DEBUG_DIRECTORY)

