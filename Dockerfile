#
# Copyright (c) 2024, Honda Research Institute Europe GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the following disclaimer in the
#  documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
FROM ubuntu:jammy-20240427

ARG WITH_SSH_SERVER
ENV USE_SSH_SERVER=$WITH_SSH_SERVER

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
      build-essential=12.9ubuntu3 \
      cmake=3.22.1-1ubuntu1.22.04.2 \
      git=1:2.34.1-1ubuntu1.11 \
      libasio-dev=1:1.18.1-1 \
      libbullet-dev=3.06+dfsg-4build2 \
      libopenscenegraph-dev=3.6.5+dfsg1-7build3 \
      libqwt-qt5-dev=6.1.4-2 \
      libxml2-dev=2.9.13+dfsg-1ubuntu0.4 \
      libzmq3-dev=4.3.4-2 \
      openssh-server=1:8.9p1-3ubuntu0.7 \
      python-is-python3=3.9.2-2 \
      python3=3.10.6-1~22.04 \
      python3-dev=3.10.6-1~22.04 \
      python3-pip=22.0.2+dfsg-1ubuntu0.4 \
      qt5-qmake=5.15.3+dfsg-2ubuntu0.2 \
      qtbase5-dev=5.15.3+dfsg-2ubuntu0.2 \
      xauth=1:1.1-1build2 && \
    rm -rf /var/lib/apt/lists/*

COPY src /attentive_support/src
COPY requirements.txt /attentive_support/requirements.txt
RUN mkdir /attentive_support/build

WORKDIR /attentive_support/build

RUN cmake /attentive_support/src/Smile -DCMAKE_INSTALL_PREFIX=/attentive_support/install && \
    make -j 8 && \
    make install

RUN pip install --no-cache-dir -r /attentive_support/requirements.txt

RUN if [ "$WITH_SSH_SERVER" = true ] ; then \
      echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
      echo "root:hri" | chpasswd && \
      mkdir /run/sshd ; \
    fi

ENTRYPOINT if [ "$USE_SSH_SERVER" = true ] ; then \
             /usr/sbin/sshd -De ; \
           else \
             /usr/bin/python -i /attentive_support/src/tool_agent.py ; \
           fi
