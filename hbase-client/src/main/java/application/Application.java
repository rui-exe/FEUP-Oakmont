package application;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.CellUtil;

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
            // Create a connection to the HBase cluster
            Connection connection = ConnectionFactory.createConnection(config);

            // Create a table object for the financial_instruments table
            TableName tableName = TableName.valueOf("financial_instruments");
            Table table = connection.getTable(tableName);

            // Create a Scan object to scan the table
            Scan scan = new Scan();

            // Specify the column family to retrieve
            scan.addFamily(Bytes.toBytes("info"));

            // Perform the scan and retrieve the result
            ResultScanner scanner = table.getScanner(scan);

            // Iterate over the scanner results and print each row
            for (Result result : scanner) {
                // Extract and print the row key
                byte[] rowKey = result.getRow();
                System.out.println("Row key: " + Bytes.toString(rowKey));

                // Extract and print the column values in the "info" family
                for (Cell cell : result.listCells()) {
                    byte[] family = CellUtil.cloneFamily(cell);
                    byte[] qualifier = CellUtil.cloneQualifier(cell);
                    byte[] value = CellUtil.cloneValue(cell);
                    System.out.println("Column family: " + Bytes.toString(family) +
                            ", Qualifier: " + Bytes.toString(qualifier) +
                            ", Value: " + Bytes.toString(value));
                }
            }

            // Close the table and connection when done
            table.close();
            connection.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
