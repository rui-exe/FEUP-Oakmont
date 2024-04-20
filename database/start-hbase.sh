cd hbase
echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
service ssh start
./bin/start-hbase.sh
./bin/local-master-backup.sh start 2 3 
./bin/local-regionservers.sh start 2 3 4 
./bin/hbase-daemon.sh start thrift
tail -f /dev/null
