package application;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Table;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.HBaseConfiguration;
import crud.TradeExecutor;
import models.Trade;
import java.io.IOException;


public class Application {

    public static void main(String[] args) {
        String zookeeperHost = System.getenv("ZOOKEEPER_HOST");
        String zookeeperPort = System.getenv("ZOOKEEPER_PORT");

        if (zookeeperHost == null || zookeeperHost.isEmpty() || zookeeperPort == null || zookeeperPort.isEmpty()) {
          throw new IllegalArgumentException("ZOOKEEPER_HOST or ZOOKEEPER_PORT environment variables are missing or empty.");
        }
        Configuration config = HBaseConfiguration.create();
        config.set("hbase.zookeeper.quorum", zookeeperHost);
        config.set("hbase.zookeeper.property.clientPort", zookeeperPort);
        try {
            Connection connection = ConnectionFactory.createConnection(config);
        
            Admin admin = connection.getAdmin();
            createTableIfNotExists(admin, "user", new String[]{"info", "trades"});
            createTableIfNotExists(admin, "portfolio", new String[]{"positions"});
            

            Table usersTable = connection.getTable(TableName.valueOf("user"));
            Table portfolioTable = connection.getTable(TableName.valueOf("portfolio"));

            TradeExecutor tradeExecutor = new TradeExecutor(usersTable, portfolioTable);

            String username = "omaior";
            long initialBalance = 1500;

            long now = System.currentTimeMillis();
            Trade buyTrade1 = new Trade(username, Trade.TradeType.BUY, "AAPL", 10, 150, now, now);
            Trade sellTrade1 = new Trade(username, Trade.TradeType.SELL, "AAPL", 11, 160, now, now);
            Trade sellTrade2 = new Trade(username, Trade.TradeType.SELL, "AAPL", 5, 300, now, now);
            Trade buyTrade2 = new Trade(username, Trade.TradeType.BUY, "AAPL", 10, 150, now, now);
            Trade sellTrade3 = new Trade(username, Trade.TradeType.SELL, "AAPL", 15, 300, now, now);

            usersTable.put(new Put(Bytes.toBytes(username)).addColumn(Bytes.toBytes("info"), Bytes.toBytes("balance"), Bytes.toBytes(initialBalance)));
            
            if (tradeExecutor.executeBuyTrade(buyTrade1)) {
                System.out.println("Trade 1 successful");
            } else {
                System.out.println("Trade 1 failed");
            }
            tradeExecutor.printUserDetails(username);

            if (tradeExecutor.executeSellTrade(sellTrade1)) {
                System.out.println("Trade 2 successful");
            } else {
                System.out.println("Trade 2 failed");
            }
            tradeExecutor.printUserDetails(username);

            if (tradeExecutor.executeSellTrade(sellTrade2)) {
                System.out.println("Trade 3 successful");
            } else {
                System.out.println("Trade 3 failed");
            }
            tradeExecutor.printUserDetails(username);

            if (tradeExecutor.executeBuyTrade(buyTrade2)) {
                System.out.println("Trade 4 successful");
            } else {
                System.out.println("Trade 4 failed");
            }
            tradeExecutor.printUserDetails(username);
 
            if (tradeExecutor.executeSellTrade(sellTrade3)) {
                System.out.println("Trade 5 successful");
            } else {
                System.out.println("Trade 5 failed");
            }

            tradeExecutor.printUserDetails(username);

            connection.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void createTableIfNotExists(Admin admin, String tableName, String[] columnFamilies) throws IOException {
        TableName table = TableName.valueOf(tableName);
        if (!admin.tableExists(table)) {
            TableDescriptorBuilder tableDescriptorBuilder = TableDescriptorBuilder.newBuilder(table);
            for (String cf : columnFamilies) {
                ColumnFamilyDescriptor columnFamilyDescriptor = ColumnFamilyDescriptorBuilder.newBuilder(Bytes.toBytes(cf)).build();
                tableDescriptorBuilder.setColumnFamily(columnFamilyDescriptor);
            }
            admin.createTable(tableDescriptorBuilder.build());
            System.out.println("Table " + tableName + " created successfully.");
        }
    }
}
