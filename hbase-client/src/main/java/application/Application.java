package application;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Increment;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.RowMutations;
import org.apache.hadoop.hbase.client.Table;
import org.apache.hadoop.hbase.filter.CompareFilter;
import org.apache.hadoop.hbase.util.Bytes;

import java.io.IOException;

public class Application {
    public static void main(String[] args) throws IOException {
        String zookeeperHost = System.getenv("ZOOKEEPER_HOST");
        String zookeeperPort = System.getenv("ZOOKEEPER_PORT");

        if (zookeeperHost == null || zookeeperHost.isEmpty() || zookeeperPort == null || zookeeperPort.isEmpty()) {
            throw new IllegalArgumentException("ZOOKEEPER_HOST or ZOOKEEPER_PORT environment variables are missing or empty.");
        }
        Configuration config = HBaseConfiguration.create();
        config.set("hbase.zookeeper.quorum", zookeeperHost);
        config.set("hbase.zookeeper.property.clientPort", zookeeperPort);


        try (Connection connection = ConnectionFactory.createConnection(config);
            Table table = connection.getTable(TableName.valueOf("user"))) {

            String username = "ssample4k";
            String userInfoCF = "info";
            String balanceQualifier = "balance";
            long initialBalance = 50;

            Put put = new Put(Bytes.toBytes(username));
            put.addColumn(Bytes.toBytes(userInfoCF), Bytes.toBytes(balanceQualifier), Bytes.toBytes(initialBalance));
            table.put(put);


            Increment increment = new Increment(Bytes.toBytes(username));
            increment.addColumn(Bytes.toBytes(userInfoCF), Bytes.toBytes(balanceQualifier), -10);
            RowMutations mutations = new RowMutations(Bytes.toBytes(username));
            mutations.add(increment);
            for (int i = 0; i < 6; i++) {
                System.out.println("Balance before iteration " + (i + 1) + ": " + getBalance(table, username, userInfoCF, balanceQualifier));
                long balance_needed = 10;
                //mutate if balance of the user >= balance_needed
                boolean transactionWentThrough = table.checkAndMutate(
                        Bytes.toBytes(username), Bytes.toBytes(userInfoCF), Bytes.toBytes(balanceQualifier),
                        CompareFilter.CompareOp.LESS_OR_EQUAL,
                        Bytes.toBytes(balance_needed),
                        mutations);

                System.out.println("Balance after iteration " + (i + 1) + ": " + getBalance(table, username, userInfoCF, balanceQualifier));

                if(!transactionWentThrough)
                    System.out.println("Not enough balance to buy this stock");
            }
        }
    }

    private static long getBalance(Table table, String username, String columnFamily, String qualifier) throws IOException {
        return table.get(new Get(Bytes.toBytes(username)))
                .getValue(Bytes.toBytes(columnFamily), Bytes.toBytes(qualifier)) != null ?
                Bytes.toLong(table.get(new Get(Bytes.toBytes(username)))
                        .getValue(Bytes.toBytes(columnFamily), Bytes.toBytes(qualifier))) : 0;
    }
}
