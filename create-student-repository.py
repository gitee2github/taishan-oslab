#!/bin/python3

import argparse
import os
import sys
import hashlib
import subprocess

import gitlab
from gitlab.v4.objects import User

args = argparse.ArgumentParser(description="Create a student gitlab account and a gitlab project.")

args.add_argument("username")
args.add_argument("name")
args.add_argument("password")
args.add_argument("pub_key")
# args.add_argument("--autoTestServerHook", default="/home/git/scripts/ostest/custom_hooks", type=str)

args = args.parse_args()

GROUP_ID = os.environ['GITLAB_GROUP_ID']
EMAIL_SUFFIX = os.environ['EMAIL_SUFFIX']
CONTAINER_NAME = os.environ['GITLAB_CONTAINER_NAME']

gl = gitlab.Gitlab(
    url=os.environ['GITLAB_URL'],
    private_token=os.environ['GITLAB_PRIVATE_TOKEN'],
    keep_base_url=True
)


def create_user(username: str, name: str, password: str) -> User:
    user = gl.users.create({
        'username': username,
        'name': name,
        'password': password,
        'email': username + EMAIL_SUFFIX,
        'skip_confirmation': True
    })
    print('Created user', user.id)
    return user


def add_key(user: User, pub_key: str):
    key = user.keys.create({'title': 'oslab', 'key': pub_key})
    print(f'{user.username}: created key', key.id)
    return key


def create_project(user: User):
    # groupID = gl.groups.list(search=GROUP_NAME)[0].id
    project = gl.projects.create({
        "name": user.username,
        "path": user.username,
        "namespace_id": GROUP_ID,
        "description": f"Project for {user.name} - {user.username}",
        "visibility": "private"
    })
    # 分配用户权限
    project.members.create({
        'user_id': user.id,
        'access_level': gitlab.const.MAINTAINER_ACCESS
    })
    print(f'{user.username}: created project {project.id}')

    # 创建自动评测脚本hook
    try:
        h = hashlib.sha256(str(project.id).encode()).hexdigest()
        path = f"/var/opt/gitlab/git-data/repositories/@hashed/{h[0:2]}/{h[2:4]}/{h}.git/custom_hooks"
        subprocess.run(
            ['docker', 'exec', CONTAINER_NAME, 'ln', '-s', '/opt/stu-hooks', path]
        ).check_returncode()
    except Exception as e:
        print(f'{user.username}: failed to link hooks: {e}', file=sys.stderr)

    return project


user = create_user(args.username, args.name, args.password)
add_key(user, args.pub_key)
create_project(user)
