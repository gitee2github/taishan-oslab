FROM openeuler/openeuler:22.03-lts

RUN dnf -y update

RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# base: no gdb here, it's provided in /OSLAB
RUN dnf -y install \
    vim nano sudo git gcc make ctags passwd openssh-server

# Languages
RUN dnf install -y golang java-latest-openjdk-devel php

# QEMU dependencies
RUN dnf -y install pixman libepoxy gtk3

RUN dnf autoremove && dnf clean all

RUN groupadd -g 1000 git && \
    useradd -ms /bin/bash -g 1000 -u 1000 git && \
    echo "git	ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -P '' && \
    ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -P '' && \
    ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -P ''

USER git

ENV RUSTUP_DIST_SERVER https://mirrors.tuna.tsinghua.edu.cn/rustup
RUN echo "export RUSTUP_DIST_SERVER=$RUSTUP_DIST_SERVER" >> ~/.bash_profile
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

USER root

COPY rpms /tmp/rpms
RUN rpm -i /tmp/rpms/*.rpm && rm -r /tmp/rpms && dnf autoremove && dnf clean all

# openEuler's PAM breaks non-root ssh sessions in a container
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# gdb
RUN ln -s libpython3.9.so.1.0 /usr/lib64/libpython3.8.so.1.0

COPY bin /tmp/bin
RUN chmod +x /tmp/bin/* && mv /tmp/bin/* /usr/bin/ && rm -r /tmp/bin

COPY vsixs /tmp/vsixs
RUN chown -R git:git /tmp/vsixs

USER git

RUN echo 'export PATH=/OSLAB/compiler/usr/bin:/OSLAB/gdb/bin:/OSLAB/qemu/usr/local/bin:$PATH' >> ~/.bashrc
RUN code-server --install-extension /tmp/vsixs/*.vsix && rm -r /tmp/vsixs
RUN git init ~/repo -b master

USER root

VOLUME ["/OSLAB"]
EXPOSE 22 10080

COPY entry /opt/os-entry

ENTRYPOINT ["/opt/os-entry"]
