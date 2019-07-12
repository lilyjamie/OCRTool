import re
import difflib


def regular_match(pattern, src_str):
    rst_str = re.match(pattern, src_str)
    if rst_str:
        print("Regular match: ")
        return True, 1.0
    else:
        print("Regular not match.")
        return False, -1.0


def is_text_match(pattern, src_str, nice, method=None):
    if not pattern:
        pattern = ''

    if not src_str:
        src_str = ''

    if method:
        method = method.lower()
        if 'br2auto-sp' in str(method):
            if '\n' in src_str:
                pattern = pattern.replace('\n', ' ')
                src_str = src_str.replace('\n', ' *')
                return regular_match(src_str, pattern)
        elif 'br2sp' in str(method):
            pattern = pattern.replace('\n', ' ')
            src_str = src_str.replace('\n', ' ')
        elif 'no-br' in str(method):
                pattern = pattern.replace('\n', '')
                src_str = src_str.replace('\n', '')

        if 'no-sp' in str(method):
            pattern = pattern.replace(' ', '')
            src_str = src_str.replace(' ', '')

        if 'substr' in str(method):
            if pattern in src_str:
                return True, 1.0
            return False, -1.0

        if 'regular' in str(method):
            return regular_match(pattern, src_str)

    if type(nice) == int:
        if not ((nice >= 0) and (nice <= 100)):
            return False, -1.0
        ratio = difflib.SequenceMatcher(None, pattern, src_str).quick_ratio()
        print('Ration:' + str(ratio))
        return ratio*100 >= nice, round(ratio, 2)
    else:
        if pattern == src_str:
            return True, 1.0
        else:
            return False, -1.0
