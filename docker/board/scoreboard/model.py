import os
import json
import logging
import sqlite3
import subprocess
from collections import namedtuple
from util import parse_dt as parse

logger = logging.getLogger("FLASK")


def read_config():
    with open('/config.json', 'r') as file:
        config = json.load(file)

    labs = config.get('labs', [])
    root = config['ostest_src']
    with os.scandir(root) as it:
        for e in it:
            name = e.name
            if not name.startswith('.') and not name.startswith('score-by') and e.is_dir() and name not in (
                'student', 'target', 'custom_hooks'
            ) and os.path.exists(os.path.join(root, name, 'judge.sh')):
                labs.append(name)

    for i, lab in enumerate(labs):
        if isinstance(lab, str):
            lab = {'title': lab}
        lab['width'] = 50
        lab['isResize'] = True
        lab['orderBy'] = ''
        if 'isExam' not in lab:
            lab['isExam'] = False
        if 'releaseDate' not in lab:
            lab['releaseDate'] = '2022-02-01T23:14:00+0800'
        if 'deadline' not in lab:
            lab['deadline'] = '2022-12-24 12:10:00'
        labs[i] = lab

    config['labs'] = labs
    config['score_src'] = os.path.join(config['ostest_src'], 'score-byuser')

    return config


config = read_config()
oslab_src = config['oslab_src']
share_src = os.path.join(oslab_src, 'data/share')

stats_url: str
stats_db: str


def read_oslab_config():
    res = subprocess.check_output(f'. {oslab_src}/config.ini && echo "$STATS_URL" && echo "$STATS_DB"', shell=True, text=True)
    res = res.strip().split('\n')

    global stats_url
    global stats_db
    stats_url, stats_db = res


read_oslab_config()
Teacher = namedtuple('Teacher', ['codename', 'zhname', 'index'])
Student = namedtuple('Student', ['teacher', 'stu', 'name', 'apikey'])
Lab = namedtuple('Lab', ['title', 'begin', 'end'])


def read_student_list():
    data = []
    con = sqlite3.connect(stats_db)
    cur = con.cursor()
    try:
        with open(os.path.join(config['oslab_src'], 'data/students')) as fp:
            for line in fp:
                s = line.strip()
                if s:
                    s = s.split()
                    stu = s[0]
                    apikey = cur.execute('SELECT api_key FROM users WHERE id = ?', (stu, )).fetchone()[0]
                    data.append(Student('teacher', stu, s[-1], apikey.encode('utf-8')))
    except FileNotFoundError:
        pass
    cur.close()
    con.close()

    return data


def read_lab_list():
    return [Lab(lab['title'], parse(lab['releaseDate']), parse(lab['deadline'])) for lab in config['labs']]


def read_teacher_list():
    return [Teacher(d['codename'], d['zhname'], i) for i, d in enumerate(config['teachers'])]


score_src = config['score_src']
lab_list = read_lab_list()

teacher_list = read_teacher_list()
teacher_dict = {
    t.codename: t for t in teacher_list
}

student_list = read_student_list()
student_dict = {
    s.stu: s for s in student_list
}


def reload_data():
    student_list.clear()
    student_list.extend(read_student_list())

    student_dict.clear()
    for s in student_list:
        student_dict[s.stu] = s
