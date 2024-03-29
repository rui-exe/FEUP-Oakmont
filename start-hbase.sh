cd hbase
./bin/start-hbase.sh
./bin/local-master-backup.sh start 2 3 5
./bin/local-regionservers.sh start 2 3 4 5
tail -f /dev/null
