FROM ubuntu:jammy-20240427

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
      build-essential=12.9ubuntu3 \
      cmake=3.22.1-1ubuntu1.22.04.2 \
      git=1:2.34.1-1ubuntu1.10 \
      libasio-dev=1:1.18.1-1 \
      libbullet-dev=3.06+dfsg-4build2 \
      libopenscenegraph-dev=3.6.5+dfsg1-7build3 \
      libqwt-qt5-dev=6.1.4-2 \
      libxml2-dev=2.9.13+dfsg-1ubuntu0.4 \
      libzmq3-dev=4.3.4-2 \
      python-is-python3=3.9.2-2 \
      python3=3.10.6-1~22.04 \
      python3-dev=3.10.6-1~22.04 \
      python3-pip=22.0.2+dfsg-1ubuntu0.4 \
      qt5-qmake=5.15.3+dfsg-2ubuntu0.2 \
      qtbase5-dev=5.15.3+dfsg-2ubuntu0.2 && \
    rm -rf /var/lib/apt/lists/*

COPY src /attentive_support/src
COPY requirements.txt /attentive_support/requirements.txt
RUN mkdir /attentive_support/build

WORKDIR /attentive_support/build

RUN cmake /attentive_support/src/Smile -DCMAKE_INSTALL_PREFIX=/attentive_support/install && \
    make -j && \
    make install

RUN pip install --no-cache-dir -r /attentive_support/requirements.txt

ENTRYPOINT [ "/usr/bin/python", "-i", "/attentive_support/src/tool_agent.py" ]
