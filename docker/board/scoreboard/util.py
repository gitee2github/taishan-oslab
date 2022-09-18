from functools import partial
from dateutil.parser import parse


def make_cst_dt():
    from datetime import datetime, time
    from dateutil import tz
    return datetime.combine(datetime.now(),
                            time(0, tzinfo=tz.gettz('Asia/Shanghai')))


parse_dt = partial(parse, default=make_cst_dt())
