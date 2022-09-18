#!/bin/python3
# Add the ssh public key for osjudge to root user.

import os
import sys
import gitlab


def main():
    with open('keys/id_rsa.pub', encoding='utf-8') as fp:
        key = fp.read().strip()

    gl = gitlab.Gitlab(
        url=os.environ['GITLAB_URL'],
        private_token=os.environ['GITLAB_PRIVATE_TOKEN'],
        keep_base_url=True
    )

    gl.auth()
    try:
        gl.user.keys.create({'title': 'osjudge', 'key': key})
    except Exception as e:
        print(f'keys.create: {e}', file=sys.stderr)


if __name__ == '__main__':
    main()
