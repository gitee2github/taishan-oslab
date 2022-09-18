#!/bin/python3

import os
import sys
import requests


def main():
    user = sys.argv[1]
    passwd = sys.argv[2]
    data = {
        'location': 'Asia/Shanghai',
        'username': user,
        'email': '',
        'password': passwd,
        'password_repeat': passwd
    }
    url = os.environ['STATS_URL'] + '/signup'
    requests.post(url, data=data).raise_for_status()


if __name__ == '__main__':
    main()
