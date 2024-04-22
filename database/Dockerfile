From ubuntu:bionic

COPY ./shell-scripts/*.sh /shell-scripts/

COPY ./start-hbase.sh /start-hbase.sh

ENV HBASE_VERSION 2.5.8

RUN /shell-scripts/prepare-hbase.sh 

ADD ./hbase-site.xml /hbase/conf/hbase-site.xml

ADD ./zoo.cfg /hbase/conf/zoo.cfg

CMD ["sh", "/start-hbase.sh"] 