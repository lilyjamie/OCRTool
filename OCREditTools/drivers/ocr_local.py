from PIL import Image
import pytesseract


class OCRLocal:
    def __init__(self):
        pass

    @staticmethod
    def _strip_text(text):
        return text.strip()

    @staticmethod
    def img_to_str(img_file_path, lang='eng', config=''):
        img = Image.open(img_file_path)
        return pytesseract.image_to_string(img, lang, config)

    @staticmethod
    def ocr_local_get_frame_text(frame, lang='eng', config=''):
        text = pytesseract.image_to_string(frame, lang, config)
        return OCRLocal._strip_text(text)

    @staticmethod
    def ocr_local_get_img_text(img_file_path, lang='eng', config=''):
        text = OCRLocal.img_to_str(img_file_path, lang, config)
        return_str = OCRLocal._strip_text(text)
        return return_str
