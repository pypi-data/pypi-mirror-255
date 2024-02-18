import httpx
import os
import random
import uuid

from time import sleep





def check_dot_ignore():
    ignore_text = '\n# Added by CryptMaster\n.crypt_file'
    file = '.gitignore'
    if os.path.isfile(file):
        with open(file, 'r') as f:
            git_ignore = f.read()
        if not '.crypt_file' in git_ignore:
            with open(file, 'a') as f:
                f.write(ignore_text)
    else:
        with open(file, 'w') as f:
            f.write(ignore_text[1:])



def get_create_config():
    crypt_file = '.crypt_file'
    if not os.path.isfile(crypt_file):
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        salt = ''
        for i in range(32):
            salt += (random.choice(ALPHABET))
        with open(crypt_file, 'w+') as f:
            f.write(salt)
        check_dot_ignore()
    with open(crypt_file, 'r') as f:
        crypt_config = f.readline()
    return crypt_config





class CryptMaster:
    def __init__(self, server, port=2053):
        self.SALT = get_create_config()
        self.system_id = uuid.getnode()
        self.server = f'https://{server}:{port}'

    def get_secret(self, requested_secret):
        payload = {"requested_password": requested_secret, 'system_id': self.system_id}
        url = f'{self.server}/get_secret'
        while True:
            response = httpx.post(url=url, json=payload, timeout=5, verify=False)
            if response.status_code != 200:
                print('Did not get a good response')
                sleep(20)
                continue
            response = response.json()
            secret = response.get('secret', None)
            status = response.get('response', None)
            if secret is not None:
                break
            else:
                print(status)
                sleep(20)
                continue
        return secret

    def enroll_server(self):
        payload = {'system_id': self.system_id, 'system_salt': self.SALT}
        url = f'{self.server}/enroll_server'
        while True:
            response = httpx.post(url=url, json=payload, timeout=5, verify=False)
            if response.status_code != 200:
                print('Did not get a good response')
                sleep(20)
                continue
            response = response.json()
            status = response.get('response', None)
            if status is not None:
                break
            else:
                print('Did not get a good response')
                sleep(20)
                continue
        return status



