package hbaseclient;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.Grpc;
import io.grpc.InsecureServerCredentials;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Table;

import java.util.concurrent.TimeUnit;
import java.io.IOException;
import java.util.logging.Logger;

public class HbaseClientServer {
    private final int port;
    private final Server server;
    private static final Logger logger = Logger.getLogger(HbaseClientServer.class.getName());
    private final Connection connection;

  

    public HbaseClientServer(int port) throws IOException {
        this.port = port;
        ServerBuilder<?> serverBuilder = Grpc.newServerBuilderForPort(port, InsecureServerCredentials.create());
        String zookeeperHost = System.getenv("ZOOKEEPER_HOST");
        String zookeeperPort = System.getenv("ZOOKEEPER_PORT");

        if (zookeeperHost == null || zookeeperHost.isEmpty() || zookeeperPort == null || zookeeperPort.isEmpty()) {
            throw new IllegalArgumentException("ZOOKEEPER_HOST or ZOOKEEPER_PORT environment variables are missing or empty.");
        }
        Configuration config = HBaseConfiguration.create();
        config.set("hbase.zookeeper.quorum", zookeeperHost);
        config.set("hbase.zookeeper.property.clientPort", zookeeperPort);
        connection = ConnectionFactory.createConnection(config);
        Table usersTable = connection.getTable(TableName.valueOf("user"));
        Table portfolioTable = connection.getTable(TableName.valueOf("portfolio"));
        Table popularityToInstrumentTable = connection.getTable(TableName.valueOf("popularity_to_instrument"));
        Table financialInstrumentsTable = connection.getTable(TableName.valueOf("financial_instruments"));

        TradeExecutorService tradeExecutorService = new TradeExecutorService(usersTable,portfolioTable,
                                                        financialInstrumentsTable,popularityToInstrumentTable);
        InstrumentAnalyticsService instrumentAnalyticsService = new InstrumentAnalyticsService(config,connection);

        serverBuilder.addService(tradeExecutorService);
        serverBuilder.addService(instrumentAnalyticsService);

        server = serverBuilder.build();
    }

    public void start() throws IOException {
        server.start();
        logger.info("Server started, listening on " + port);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
          // Use stderr here since the logger may have been reset by its JVM shutdown hook.
          System.err.println("*** shutting down gRPC server since JVM is shutting down");
          try {
              HbaseClientServer.this.stop();
          } catch (InterruptedException e) {
            e.printStackTrace(System.err);
          }
          System.err.println("*** server shut down");
        }));
    }

    public void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    public static void main(String[] args) throws Exception {
        String portStr = System.getenv("HBASE_CLIENT_SERVER_PORT");
        if (portStr == null || portStr.isEmpty()) {
            throw new IllegalArgumentException("HBASE_CLIENT_SERVER_PORT environment variables are missing or empty.");
        }
        int port = Integer.parseInt(System.getenv("HBASE_CLIENT_SERVER_PORT"));
        HbaseClientServer server = new HbaseClientServer(port);
        server.start();
        server.blockUntilShutdown();
    }

}
