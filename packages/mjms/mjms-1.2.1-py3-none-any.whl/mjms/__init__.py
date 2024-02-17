from typing import List, Union
import requests

class MJMS(object):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = 'https://mailsrv.marcusj.org/api'

    def send_mail(self, to: Union[List, str], subject: str, html: str=None, text: str=None):
        r = requests.post(f'{self.base}/mail/send', json={
            'key': self.api_key,
            'to': to,
            'subject': subject,
            'html': html or text
        })
        return r.json()
    
    def verify_email(self, to: str):
        r = requests.post(f'{self.base}/mail/verify/send', json={
            'key': self.api_key,
            'to': to,
        })
        return r.json()
    
    def check_verified(self, token: str):
        r = requests.post(f'{self.base}/mail/verify/check', json={
            'key': self.api_key,
            'token': token
        })
        return r.json()