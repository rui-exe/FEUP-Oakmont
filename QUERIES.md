## Hbase Shell Queries

### Setup
Before runnning the following commands, make sure that the docker container is running, and that the database is populated.
Run the following commands to access the HBase shell:
```shell
docker exec -it hadoop bash
cd /usr/local/hbase/bin/
./hbase shell
```
After that import this class to use the Bytes.toBytesBinary method:
```shell
import org.apache.hadoop.hbase.util.Bytes
```

### Authentitcation

* Get the user (ssample4) info to check if a the username and password are correct
```shell
get 'user', 'ssample4', 'info'
```

* Create a new user with the username  password name and email (ssample10, , 1234, sample,ssample10@gmail.com) and get the new user info
```shell    
put 'user', 'ssample10', 'info:name', 'sample'
put 'user', 'ssample10', 'info:password', '$2b$12$uqT6QX.6t.5cZvke1iVVTu3iT7VEGZMG2dWNA9m.qE5NA.TvBCVly'
put 'user', 'ssample10', 'info:email', 'ssample10@gmail.com'
get 'user', 'ssample10', 'info'
```

### Price Information

* Get the most recent price of the stock (AAPL)
>**_NOTE:_** There is in fact a bug in the hbase shell that is not possible to use the reverse order in the scan command when a row prefix is used. The solution is to use StartRow and EndRow. The bug is documented in the following link: https://issues.apache.org/jira/browse/HBASE-16886?jql=project%20%3D%20HBASE. It appears that the bug was fixed as the status is Closed but it is still present.
```shell
scan 'instrument_prices', {STARTROW => 'AAPL`', ENDROW => 'AAPL_', LIMIT => 1, REVERSED => true}
```

* Retrieve historical prices and variation of an item across various time intervals (last week, month, year) with different levels of detail (per minute, hour, day)

This is actually not possible to do in the hbase shell. Is necessary to use the MapReduce witch is not possible to use in the hbase shell. The solution is to use the Hadoop MapReduce.

* Price updates for a stock (AAPL)
```shell
put 'instrument_prices', Bytes.toBytesBinary("AAPL_\x00\x00\x01\xb8\xda\xc5\xb4\x00"), 'series:val', '100'
scan 'instrument_prices', {STARTROW => 'AAPL`', ENDROW => 'AAPL_', LIMIT => 1, REVERSED => true}
```

### Post Management

* See all the posts for a given a financial instrument (AAPL)
```shell
scan 'financial_instruments', {ROWPREFIXFILTER => 'AAPL', COLUMNS => 'posts'}
```

* See all the posts of a given user (ssample4)
```shell
scan 'user', {ROWPREFIXFILTER => 'ssample4', COLUMNS => 'posts'}
```

* Create a new post for a given user (ssample4) and financial instrument (AAPL)
```shell
put 'user', 'ssample4', "posts:\x7f\xff\xfem\x87V\xea\x7f", "{\"symbol\":\"AAPL\",\"post\":\"This is a new post.\",\"post_id\":\"100000\"}"
put 'financial_instruments', 'AAPL', "posts:\x7f\xff\xfem\x87V\xea\x7f", "{\"username\":\"ssample4\",\"post\":\"This is a new post.\", \"post_id\":\"100000\"}"
```

### User Interaction

* See all the followers/following of a given user (ssample4)
```shell
get 'user', 'ssample4', {COLUMN => 'followers'}
get 'user', 'ssample4', {COLUMN => 'following'}
```

* Follow a user (ssample4) from another user (ssample10)
```shell
put 'user', 'ssample4', 'followers:ssample10', '1'
incr 'user', 'ssample4', 'info:followers', 1
incr 'user', 'ssample10', 'info:following', 1
put 'user', 'ssample10', 'following:ssample4', '1'
```

### Item Management

*Get the most popular financial instruments
```shell
scan 'popularity_to_instrument', {LIMIT => 10}
```

* Descriptive statistics for a given item like Day's Range, 52 Week Range, Mean, etc.
This is actually not possible to do in the hbase shell. Is necessary to use the MapReduce witch is not possible to use in the hbase shell. The solution is to use the Hadoop MapReduce.

* Look up the financial instrument (AAPL) by its symbol
```shell
get 'financial_instruments', 'AAPL'
```

### Portfolio Management

* Retrieve a user's portfolio (ssample4).
```shell
scan 'portfolio', { FILTER => "PrefixFilter('ssample4_')" }
```

* See a user's trading history.
```shell
scan 'user', { STARTROW => 'ssample4', ENDROW => 'ssample4+', COLUMN => 'trades'}
```

### Transaction Management

* Buy a stock (AAPL) for a user (ssample4) and update the user's portfolio.
This is actually not possible to do in the hbase shell. Is necessary the use of transactions witch is not possible to use in the hbase shell. 

* Add funds (10$) to a user's account (ssample4) and update the user's balance. Notice that the value is multiplied by 100 because the hbase counter are integers, so the value is multiplied by 100 to store the cents, and then in the application, the value is divided by 100 to get the dollars.
```shell
incr 'user', 'ssample4', 'info:balance', 1000
```
