service ssh start

export HADOOP_HOME=/usr/local/hadoop
export HBASE_HOME=/usr/local/hbase

echo "================================================================================"
echo "                              Hadoop Docker Container                           "
echo "================================================================================"
echo


cleanup(){
    pgrep -f master && pkill -9 -f master
    pgrep -f regionserver && pkill -9 -f regionserver
    pgrep -f proc_thrift && pkill -9 -f proc_thrift
}

start_dfs(){
    echo "Starting HDFS..."
    
    if [ ! -d "/hdfs/namenode/" ]; then
        echo "Creating /hdfs/namenode/ directory..."
        mkdir -p "/hdfs/namenode/"
    fi
    
    # Create /hdfs/datanode/ directory if it doesn't exist
    if [ ! -d "/hdfs/datanode/" ]; then
        echo "Creating /hdfs/datanode/ directory..."
        mkdir -p "/hdfs/datanode/"
    fi

    if [ ! -d "/hdfs/namenode/current" ] || [ -z "$(ls -A /hdfs/namenode/current)" ]; then
        echo "Formatting NameNode..."
        yes "Y" | ${HADOOP_HOME}/bin/hdfs namenode -format
    else
        echo "NameNode repository is not empty. Skipping formatting."
    fi
    ${HADOOP_HOME}/sbin/start-dfs.sh
}

start_yarn(){
    echo "Starting YARN..."
    $HADOOP_HOME/sbin/start-yarn.sh
}

start_master(){
    echo "Starting HBase Master..."
    "$HBASE_HOME/bin/start-hbase.sh"
    "$HBASE_HOME/bin/local-master-backup.sh" start 2 3 
}


start_regionservers(){
    echo "Starting HBase RegionServers..."
    "$HBASE_HOME/bin/local-regionservers.sh" start 2 3 4 
}


start_thrift(){
    echo "Starting HBase Thrift API server..."
    "$HBASE_HOME/bin/hbase-daemon.sh" start thrift
    echo
}

trap_func(){
    echo -e '\n\nShutting down HBase:'
    "$HBASE_HOME/bin/hbase-daemon.sh" stop thrift || :
    "$HBASE_HOME/bin/local-regionservers.sh" stop 2 3 4 || :
    "$HBASE_HOME/bin/local-master-backup.sh" stop 2 3 || :
    "$HBASE_HOME/bin/stop-hbase.sh"
}

trap trap_func INT QUIT TRAP ABRT TERM EXIT



cleanup
start_dfs
start_yarn
start_master
start_regionservers
start_thrift

tail -f /dev/null
