#!/bin/python3

import gitlab
import argparse
import os

args = argparse.ArgumentParser(description="Delete a student gitlab account and a gitlab project.")

args.add_argument("username")
args = args.parse_args()

GROUP_NAME = os.environ['GITLAB_GROUP_NAME']

gl = gitlab.Gitlab(
    url=os.environ['GITLAB_URL'],
    private_token=os.environ['GITLAB_PRIVATE_TOKEN'],
    keep_base_url=True
)


def delete_user(username: str):
    user = gl.users.list(username=username)[0]
    i = user.id
    user.delete()
    print(f'{username}: deleted user', i)


def delete_project(username: str):
    project = gl.projects.get(GROUP_NAME + '/' + username)
    i = project.id
    project.delete()
    print(f'{username}: deleted project {i}')


username = args.username
try:
    delete_project(username)
except Exception as e:
    print(f'\033[31m{username}: failed to delete project: {e}\033[0m')

try:
    delete_user(username)
except Exception as e:
    print(f'\033[31m{username}: failed to delete user: {e}\033[0m')
