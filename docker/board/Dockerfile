FROM openeuler/openeuler:22.03-lts

RUN dnf -y update

RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN dnf -y install python3
RUN dnf autoremove && dnf clean all

RUN python3 -m venv /venv
RUN /venv/bin/pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN /venv/bin/pip install -U pip wheel setuptools

COPY scoreboard/requirements.txt /tmp/requirements.txt
RUN /venv/bin/pip install -U -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY scoreboard /app
WORKDIR /app

VOLUME ["/config.json"]
EXPOSE 80
ENTRYPOINT ["/venv/bin/gunicorn", "scoreboard:app", "-b", "0.0.0.0:80"]
