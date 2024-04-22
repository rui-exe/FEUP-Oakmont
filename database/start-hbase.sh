echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
service ssh start

export HBASE_HOME="/hbase"

echo "================================================================================"
echo "                              HBase Docker Container"
echo "================================================================================"
echo


cleanup(){
    pgrep -f master && pkill -9 -f master
    pgrep -f regionserver && pkill -9 -f regionserver
    pgrep -f proc_thrift && pkill -9 -f proc_thrift
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
start_master
start_regionservers
start_thrift

tail -f /dev/null
