FROM openeuler/openeuler:22.03-lts

RUN dnf -y update

RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN dnf -y install \
    vim nano sudo git gcc gdb make ctags passwd openssh-server

# Required by QEMU
RUN dnf -y install pixman libepoxy gtk3

RUN dnf -y install docker-engine

RUN dnf autoremove && dnf clean all

RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -P '' && \
    ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -P '' && \
    ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -P '' && \
    mkdir -p /root/.ssh && \
    git config --global user.email "osjudge@example.com" && \
    git config --global user.name "OS Judge"

VOLUME ["/opt/ostest"]
EXPOSE 22

COPY entry /opt/entry
ENTRYPOINT ["/opt/entry"]
