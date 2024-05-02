From ubuntu:bionic

COPY ./shell-scripts/*.sh /shell-scripts/

COPY ./config/ /tmp/

COPY ./start.sh /start.sh

ENV HBASE_VERSION 2.5.8

ENV HADOOP_VERSION 3.4.0

RUN /shell-scripts/prepare.sh 

CMD ["sh", "/start.sh"] 