import datetime
import logging
import os
import time
from sys import platform


class Util:
    is_vpn = False

    @classmethod
    def between(cls, source, prefix, suffix=None):
        p = source.find(prefix)
        if p == -1:
            return ''

        if not suffix:
            return source[p + len(prefix):]

        s = source[p + len(prefix):].find(suffix)
        if s == -1:
            return ''

        return source[p + len(prefix):p + len(prefix) + s]

    @classmethod
    def check_vpn(cls):
        ping_host = 'www.google.com'
        ping_parm = '-n' if platform == 'win32' else '-c'
        for _ in range(3):
            result = os.system('ping {} 1 {} > NUL'.format(ping_parm, ping_host))
            if result == 0:
                Util.is_vpn = True
                break
            time.sleep(5)
        logging.info('VPN: {}'.format(Util.is_vpn))
        return Util.is_vpn

    @classmethod
    def extract_number(cls, str_, index=0):
        numbers = [int(s) for s in str_.split() if s.isdigit()]
        return numbers[index]

    @classmethod
    def check_file_time(cls, path, delta=30):    # delta의 단위는 day.
        try:
            t = os.path.getmtime(path)
            last_modify_time = datetime.datetime.fromtimestamp(t)
            return (datetime.datetime.today() - last_modify_time).days < delta
        except (Exception,):
            pass
        return False
