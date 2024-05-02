#!/bin/sh -xe

. /shell-scripts/config.sh

apt-get update -y

apt-get install $minimal_apt_get_args $BUILD_PACKAGES $BUILD_RUN_PACKAGES


curl --insecure $HBASE_DIST/$HBASE_VERSION/hbase-$HBASE_VERSION-bin.tar.gz | tar -x -z && mv hbase-${HBASE_VERSION} /usr/local/hbase
curl --insecure $HADOOP_DIST-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz | tar -x -z && mv hadoop-${HADOOP_VERSION} /usr/local/hadoop


export HADOOP_HOME=/usr/local/hadoop
export HBASE_HOME=/usr/local/hbase
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HBASE_HOME/bin

ssh-keygen -t rsa -N "" -f $HOME/.ssh/id_rsa
cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys
mv /tmp/ssh_config $HOME/.ssh/config

mv /tmp/core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
mv /tmp/hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
mv /tmp/mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml
mv /tmp/yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml

mv /tmp/hbase/hbase-site.xml $HBASE_HOME/conf/hbase-site.xml
mv /tmp/hbase/zoo.cfg $HBASE_HOME/conf/zoo.cfg


# Set Java home for hbase servers
sed -i "s,^. export JAVA_HOME.*,export JAVA_HOME=$JAVA_HOME," $HBASE_HOME/conf/hbase-env.sh

# Set Java home for hadoop
sed -i "s,^. export JAVA_HOME.*,export JAVA_HOME=$JAVA_HOME," $HADOOP_HOME/etc/hadoop/hadoop-env.sh

sed -i '/^export HDFS_NAMENODE_USER=.*/{s/.*/export HDFS_NAMENODE_USER=root/;h};${x;/^$/{s//export HDFS_NAMENODE_USER=root/;H};x}' $HADOOP_HOME/etc/hadoop/hadoop-env.sh
sed -i '/^export HDFS_DATANODE_USER=.*/{s/.*/export HDFS_DATANODE_USER=root/;h};${x;/^$/{s//export HDFS_DATANODE_USER=root/;H};x}' $HADOOP_HOME/etc/hadoop/hadoop-env.sh
sed -i '/^export HDFS_SECONDARYNAMENODE_USER=.*/{s/.*/export HDFS_SECONDARYNAMENODE_USER=root/;h};${x;/^$/{s//export HDFS_SECONDARYNAMENODE_USER=root/;H};x}' $HADOOP_HOME/etc/hadoop/hadoop-env.sh
sed -i '/^export YARN_RESOURCEMANAGER_USER=.*/{s/.*/export YARN_RESOURCEMANAGER_USER=root/;h};${x;/^$/{s//export YARN_RESOURCEMANAGER_USER=root/;H};x}' $HADOOP_HOME/etc/hadoop/hadoop-env.sh
sed -i '/^export YARN_NODEMANAGER_USER=.*/{s/.*/export YARN_NODEMANAGER_USER=root/;h};${x;/^$/{s//export YARN_NODEMANAGER_USER=root/;H};x}' $HADOOP_HOME/etc/hadoop/hadoop-env.sh


# Set interactive shell defaults
cat > /etc/profile.d/defaults.sh <<EOF
JAVA_HOME=$JAVA_HOME
export JAVA_HOME
EOF

cd /usr/bin
ln -sf $here/bin/* .

cd /

# Remove build-time dependencies
apt-get remove --purge -y $BUILD_PACKAGES

# Install the run-time dependencies
apt-get install $minimal_apt_get_args $RUN_PACKAGES


chmod 744 -R $HADOOP_HOME
chmod 744 -R $HBASE_HOME

# Set correct permissions for SSH files
chmod 700 $HOME/.ssh
chmod 600 $HOME/.ssh/authorized_keys


rm -rf /tmp/* /var/tmp/*

apt-get clean
rm -rf /var/lib/apt/lists/*