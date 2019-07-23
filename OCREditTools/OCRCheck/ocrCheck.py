from TVHybridTestLibrary.keywords.ocr import *


class OCRCheck(OCR):
    def __init__(self):
        super(OCRCheck, self).__init__('')

    def create_checkpoint(self, config_name, config_value):
        temp_ckp = {config_name: config_value}
        self.checkpoints.update(temp_ckp)
