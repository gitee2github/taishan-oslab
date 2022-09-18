#!/bin/python3

import os
import gitlab

GROUP_NAME = os.environ['GITLAB_GROUP_NAME']
BASE_REPO_PATH = os.environ['BASE_REPO_PATH']

gl = gitlab.Gitlab(
    url=os.environ['GITLAB_URL'],
    private_token=os.environ['GITLAB_PRIVATE_TOKEN'],
    keep_base_url=True
)


def main():
    print('Initializing groups...')
    group = gl.groups.create({
        'name': GROUP_NAME,
        'path': GROUP_NAME,
    })
    gid = group.get_id()
    print(f'os_group: {gid}')
    public, base = BASE_REPO_PATH.split('/')
    public_group = gl.groups.create({
        'name': public,
        'path': public,
        'visibility': 'internal'
    })
    pgid = public_group.get_id()
    print(f'public_group: {pgid}')
    base_project = gl.projects.create({
        'name': base,
        'path': base,
        'namespace_id': pgid,
        'visibility': 'internal'
    })
    print(f'base_project: {base_project.get_id()}')
    os.makedirs('data', exist_ok=True)
    with open('data/gid', 'w', encoding='utf-8') as fp:
        fp.write(str(group.get_id()))


if __name__ == '__main__':
    main()
