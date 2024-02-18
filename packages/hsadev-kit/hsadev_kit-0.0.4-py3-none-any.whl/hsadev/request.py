import urllib3
import requests
from requests import utils
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Request:
    DEF_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 ' \
                'Safari/537.36 Edg/110.0.1587.46'

    def __init__(self):
        self.__headers = requests.utils.default_headers()
        self.__proxy = None
        self.__client = None

    # private functions
    def __request(self, url, timeout=30, is_get=True, data=None, json_data=None, files=None):
        if is_get:
            response = requests.get(url,
                                    proxies=self.__proxy,
                                    headers=self.__headers,
                                    verify=False,
                                    allow_redirects=True,
                                    timeout=timeout) \
                if self.__client is None else self.__client.get(url)
        else:
            response = requests.request("POST",
                                        url,
                                        proxies=self.__proxy,
                                        headers=self.__headers,
                                        verify=False,
                                        data=data,
                                        files=files,
                                        json=json_data,
                                        allow_redirects=True,
                                        timeout=timeout) \
                if self.__client is None else self.__client.post(url, params=json_data)

        if response.status_code != 200:
            raise Exception('Invalid response status: {}'.format(response.status_code))

        if 'Set-Cookie' in response.headers:
            set_cookie = response.headers.get('Set-Cookie')
            self.__headers['Cookie'] = set_cookie

        if 'Content-Type' in response.headers:
            if response.headers.get('Content-Type') == 'text/html':
                response = BeautifulSoup(response.text, 'html.parser')

        return response

    # public functions
    def set_header(self, headers, clear=True, save_cookie=False):
        if save_cookie and 'Cookie' in self.__headers:
            headers['Cookie'] = self.__headers['Cookie']

        if clear:
            self.__headers = requests.utils.default_headers()

        self.__headers['User-Agent'] = self.DEF_AGENT
        for k, v in headers.items():
            self.__headers[k] = v

    def set_proxy(self, proxy):
        self.__proxy = proxy

    def set_client(self, client):
        self.__client = client

    def get(self, url, timeout=30):
        return self.__request(url, timeout)

    def post(self, url, timeout=30, data=None, json_data=None, files=None):
        return self.__request(url, timeout, False, data, json_data, files)


# unit test
if __name__ == "__main__":
    pass
