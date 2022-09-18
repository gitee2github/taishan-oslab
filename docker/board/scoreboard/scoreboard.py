# _*_ encoding: utf-8 _*_
import base64
import logging
import os
import json

import requests
from flask import Flask, request, jsonify, Response
from flask import render_template
from flask_httpauth import HTTPBasicAuth
from flask_caching import Cache

from util import parse_dt as parse
from model import config, student_list, lab_list, teacher_list, student_dict, teacher_dict, share_src, stats_url
from lab_stat import make_teacher_stats, make_lab_stats, make_csv

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
auth = HTTPBasicAuth()
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
logger = logging.getLogger("FLASK")


@auth.get_password
def get_password(username):
    """
    :param username: username
    :return: if exist return corresponding password, and otherwise return None
    """
    for user in config['users']:
        if user['username'] == username:
            return user['password']
    return None


def read_students_info():
    data = []
    src = config['score_src']
    labs = config['labs']
    for student in student_list:
        item = student._asdict()
        del item['apikey']
        for lab in labs:
            path = os.path.join(src, item['stu'] + '/' + lab['title'])
            value = 0
            dtime = ''
            # deadline = time.mktime(parse(lab['deadline']).timetuple())
            passscore = 0
            passtime = ''
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f.readlines():
                        values = line.split()
                        if len(values) > 1 and int(values[0]) <= 120 and value < int(values[0]):
                            value = int(values[0])
                            dtime = values[1]
                            if value <= 120 and value > 100:
                                value = 100
                        if len(values) > 1 and passscore == 0 and int(values[0]) >= 60:
                            passscore = int(values[0])
                            passtime = values[1]
            item[lab['title']] = value
            item[lab['title'] + '.time'] = dtime
            item[lab['title'] + '.passscore'] = passscore
            item[lab['title'] + '.passtime'] = ''
            if passtime != '':
                item[lab['title'] + '.passtime'] = parse(passtime).strftime("%Y-%m-%d %H:%M:%S")
            item[lab['title'] + '.deadline'] = lab['deadline']
        data.append(item)
    return data


def read_score_log(uid):
    data = []
    src = config['score_src']
    labs = config['labs']
    for lab in labs:
        path = os.path.join(src, str(uid) + '/' + lab['title'])
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f.readlines():
                    values = line.split()
                    data.append({
                        'score': int(values[0]),
                        'time': parse(values[1]).strftime("%Y-%m-%d %H:%M:%S"),
                    })
    return data


@app.route('/')
@auth.login_required
@cache.cached(timeout=3600)
def index():
    return render_template('index.html')


@app.route('/json/scores')
@auth.login_required
@cache.cached(timeout=10)
def scores():
    columns = [{'title': 'stu', 'title': '学号',
                "width": 100, 'isResize': True, 'isFrozen': True}]
    columns.extend(config['labs'])
    res = {'teachers': config['teachers'],
           'columns': columns, 'students': read_students_info()}
    return json.dumps(res)


@app.route('/json/scorelog/<uid>')
@auth.login_required
@cache.cached(timeout=10)
def score_log(uid):
    return json.dumps(read_score_log(uid))


@app.route('/json/lab')
@auth.login_required
def lab():
    title = request.args.get('id')
    labs = []
    res = {
        'labs': labs
    }
    info = None
    the_lab = None
    for lab in lab_list:
        lab_title = lab.title
        labs.append(lab_title)
        if lab_title == title:
            res['info'] = info = {
                'begin': lab.begin.isoformat(),
                'end': lab.end.isoformat()
            }
            the_lab = lab

    if info is not None:
        teacher_stats = make_teacher_stats(the_lab)
        info['teachers'] = [{
            'codename': t.codename,
            'zhname': t.zhname,
            'stat': teacher_stats[t.index].render()
        } for t in teacher_list]

    return jsonify(res)


@app.route('/json/all_students')
@auth.login_required
def all_students():
    return jsonify({
        'students': [{
            'id': s.stu,
            'name': s.name,
            'teacher': s.teacher
        } for s in student_list
        ],
        'teachers': [{
            'codename': t.codename,
            'zhname': t.zhname
        } for t in teacher_list
        ]
    })


@app.route('/json/student/<stu_id>')
@auth.login_required
def student(stu_id):
    stu = student_dict[stu_id]

    file = os.path.join(share_src, stu_id, 'open.log')
    opens = []
    lim = 100
    try:
        with open(file, encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                p = line.find(' ')
                if p >= 0:
                    try:
                        opens.append([int(line[:p]), line[p + 1:]])
                    except ValueError:
                        pass

                lim -= 1
                if lim <= 0:
                    break
    except OSError as e:
        logging.error('opens %s: %s', stu_id, e, exc_info=e)
    else:
        opens.reverse()

    return jsonify({
        'name': stu.name,
        'labs': make_lab_stats(stu),
        'stu_num': len(student_list),
        'teacher': teacher_dict[stu.teacher].zhname,
        'opens': opens
    })


@app.route('/json/stats/<stu_id>')
@auth.login_required
def stats(stu_id):
    stu = student_dict[stu_id]

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(stu.apikey).decode('ascii'),
    }
    resp = requests.get(stats_url + '/api/compat/wakatime/v1/users/current/stats/all_time', headers=headers)
    try:
        resp.raise_for_status()
        stats = resp.content
    except Exception as e:
        err = f'{e}: ' + resp.text.strip()
        logging.error('stats %s: %s', stu_id, err)
        return jsonify({'error': err})

    return app.response_class(
        response=stats,
        status=200,
        mimetype='application/json'
    )


@app.route("/get_csv")
@auth.login_required
def get_csv():
    blob = make_csv().encode('utf-8')
    return Response(blob, mimetype='text/csv')


__import__('flask_cors').CORS(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
