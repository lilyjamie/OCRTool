from aip import AipOcr


class OCRCloud:
    def __init__(self):
        self.__APP_ID = '15645370'
        self.__API_KEY = 'SYnOgiO8bk650qhfzHGQbyXR'
        self.__SECRET_KEY = '2hxGZ46rID7D15HDUcsciEEfn9SZd583'
        self._client = AipOcr(self.__APP_ID, self.__API_KEY, self.__SECRET_KEY)

    @staticmethod
    def __get_file_content(file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    def ocr_cloud_get_img_text(self, img_file_path, lang='eng', config=''):
        image = self.__get_file_content(img_file_path)
        options = {}
        if config.lower() == str('general'):
            options["language_type"] = lang.upper()
            options["detect_language"] = "false"

        options["detect_direction"] = "false"
        options["probability"] = "false"
        if config.lower() == str('general'):
            msg = self._client.basicGeneral(image, options)
        else:
            msg = self._client.basicAccurate(image, options)
        text = ' '
        if msg and ('words_result' in msg.keys()):
            for i in msg.get('words_result'):
                text += i.get('words')
        return text.strip()
