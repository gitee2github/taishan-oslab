import os
import csv
from datetime import datetime
from io import StringIO

from model import teacher_list, student_list, score_src, teacher_dict, Lab, Student, lab_list
from util import parse_dt


class DurationStat:
    def __init__(self, begin: datetime):
        self.begin = begin
        self.durs = []

    def push(self, dt: datetime):
        self.durs.append((dt - self.begin).total_seconds())


class LabClassStat:
    def __init__(self, teacher, lab):
        self.teacher = teacher

        self.stu_num = 0
        self.stu_num_passed = 0
        self.stu_num_full = 0
        self.stu_num_zero = 0

        self.sub_num = 0
        self.sub_num_before_passed = 0
        self.sub_num_before_full = 0

        self.passed_stat = DurationStat(lab.begin)
        self.full_stat = DurationStat(lab.begin)
        self.any_stat = DurationStat(lab.begin)

        self.final_scores = []

    def render(self):
        return {
            'stu_num': self.stu_num,
            'stu_num_passed': self.stu_num_passed,
            'stu_num_full': self.stu_num_full,
            'stu_num_zero': self.stu_num_zero,
            'sub_num': self.sub_num,
            'sub_num_before_passed': self.sub_num_before_passed,
            'sub_num_before_full': self.sub_num_before_full,
            'passed_durs': self.passed_stat.durs,
            'full_durs': self.full_stat.durs,
            'any_durs': self.any_stat.durs,
            'final_scores': self.final_scores,
        }


class StuLabLog:
    def __init__(self, stu: Student, lab: Lab):
        file = os.path.join(score_src, stu.stu, lab.title)
        self.lab = lab
        self.scores = scores = []
        try:
            with open(file, encoding='utf-8') as fp:
                for line in fp:
                    try:
                        score, time = line.split()
                        score = int(score)
                        dt = parse_dt(time)
                    except Exception:
                        # The line is not completely written
                        pass
                    else:
                        scores.append((score, dt))
        except FileNotFoundError:
            pass

        # The lines are not granted to be sorted
        scores.sort(key=lambda x: x[1])
        self.count = len(scores)

    def teacher_stat(self):
        first_passed = None
        first_full = None
        final_score = 0
        # end = self.lab.end

        for count, (score, dt) in enumerate(self.scores, 1):
            if first_passed is None and score >= 60:
                first_passed = dt, count
            if first_full is None and score >= 100:
                first_full = dt, count
            # if dt < end and score > final_score:
            if score > final_score:
                final_score = score

        return first_passed, first_full, final_score

    def final_stat(self):
        final_score = 0
        final_score_dt = self.lab.begin
        # end = self.lab.end

        for score, dt in self.scores:
            # if dt < end:
            if score > final_score:
                final_score = score
                final_score_dt = dt
            # else:
            #     break

        return final_score, final_score_dt

    def render(self):
        return [
            (score, dt.isoformat())
            for score, dt in self.scores
        ]

    def max_score(self):
        return max(t[0] for t in self.scores) if self.scores else 0


def make_teacher_stats(lab: Lab):
    teacher_stats = [LabClassStat(t.codename, lab) for t in teacher_list]

    for stu in student_list:
        log = StuLabLog(stu, lab)
        first_passed, first_full, final_score = log.teacher_stat()
        count = log.count
        scores = log.scores

        stat = teacher_stats[teacher_dict[stu.teacher].index]
        stat.stu_num += 1
        if final_score >= 60:
            stat.stu_num_passed += 1
            if final_score >= 100:
                stat.stu_num_full += 1
        elif final_score == 0:
            stat.stu_num_zero += 1

        stat.sub_num += count
        stat.sub_num_before_passed += count if first_passed is None else first_passed[1]
        stat.sub_num_before_full += count if first_full is None else first_full[1]

        if first_passed:
            stat.passed_stat.push(first_passed[0])
        if first_full:
            stat.full_stat.push(first_full[0])
        if scores:
            stat.any_stat.push(scores[0][1])

        stat.final_scores.append(final_score)

    return teacher_stats


def make_lab_stats(stu: Student):
    res = []
    for lab in lab_list:
        stu_scores = []
        for s in student_list:
            log = StuLabLog(s, lab)
            stu_scores.append((s, log, log.final_stat()))

        stu_scores.sort(key=lambda t: (-t[2][0], t[2][1], t[0].stu))

        rank = None
        log = None
        for rk, (stu_cur, log_cur, _) in enumerate(stu_scores):
            if stu is stu_cur:
                rank = rk + 1
                log = log_cur

        res.append({
            'lab': lab.title,
            'begin': lab.begin.isoformat(),
            'end': lab.end.isoformat(),
            'rank': rank,
            'log': log.render()
        })

    return res


coefs = (
    None,
    (15, 0.5),
    (20, 1),
    (20, 1),
    (5, 0.5),
    (5, 0.5)
)


def make_csv():
    fp = StringIO()
    w = csv.writer(fp)
    w.writerow(['学号', '姓名'] + [lab.title for lab in lab_list] + ['总成绩'])
    for stu in student_list:
        row = [stu.stu, stu.name]
        d = {}
        for lab in lab_list:
            log = StuLabLog(stu, lab)
            v = log.max_score()
            row.append(v)
            d[lab.title] = v

        w.writerow(row)

    return fp.getvalue()
