package hbaseclient;

import com.google.protobuf.Timestamp;
import io.grpc.stub.StreamObserver;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.hbase.mapreduce.TableReducer;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.mapreduce.Job;
import proto.hbaseclient.InstrumentAnalyticsGrpc;
import proto.hbaseclient.InstrumentPricesRequest;
import proto.hbaseclient.InstrumentPricesResponse;
import proto.hbaseclient.Tick;

import java.io.IOException;
import java.util.UUID;

public class InstrumentAnalyticsService extends InstrumentAnalyticsGrpc.InstrumentAnalyticsImplBase {

    private final Configuration conf;
    private final Connection connection;
    public static final byte[] RESULT_CF = "cf".getBytes();
    public static final byte[] RESULT_COLUMN_QUALIFIER = "count".getBytes();


    public InstrumentAnalyticsService(Configuration conf,Connection connection) {
        this.conf = conf;
        this.connection = connection;
    }

    @Override
    public void getInstrumentPrices(InstrumentPricesRequest request, StreamObserver<InstrumentPricesResponse> responseObserver) {
        try {
            InstrumentPricesResponse response = calculateAggregatedPrices(request);
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        } catch (IOException | InterruptedException | ClassNotFoundException e) {
            e.printStackTrace();
            responseObserver.onError(e);
        }
    }


    private void createTable(String name) throws IOException {
        Admin admin = connection.getAdmin();
        TableDescriptor tableDescriptor = TableDescriptorBuilder.newBuilder(TableName.valueOf(name)).build();
        admin.createTable(tableDescriptor);
        admin.close();
    }

    private void deleteTable(String name) throws IOException{
        Admin admin = connection.getAdmin();
        admin.disableTable(TableName.valueOf(name));
        admin.deleteTable(TableName.valueOf(name));
        admin.close();
    }

    private InstrumentPricesResponse calculateAggregatedPrices(InstrumentPricesRequest request) throws IOException, InterruptedException, ClassNotFoundException {
        String randomTableName = "tmp_" + UUID.randomUUID().toString().replace("-", "");
        createTable(randomTableName);
        conf.setLong("delta", request.getTimeDelta().getSeconds()*1000);
        Job job = Job.getInstance(conf, "CalculateInstrumentPrices");
        job.setJarByClass(InstrumentAnalyticsService.class);
        Scan scan = new Scan();
        scan.withStartRow(Bytes.toBytes(request.getSymbol() + "_" + request.getStartDate().getSeconds() * 1000));
        scan.withStopRow(Bytes.toBytes(request.getSymbol() + "_" + request.getEndDate().getSeconds() * 1000),true);
        TableMapReduceUtil.initTableMapperJob(
                "instrument_prices",        // input table
                scan,               // Scan instance to control CF and attribute selection
                PriceMapper.class,     // mapper class
                LongWritable.class,         // mapper output key
                DoubleWritable.class,  // mapper output value
                job);

        TableMapReduceUtil.initTableReducerJob(
                randomTableName,        // output table
                PriceReducer.class,    // reducer class
                job);

        boolean b = job.waitForCompletion(true);
        if (!b) {
            throw new IOException("error with job!");
        }

        Table resultTable = connection.getTable(TableName.valueOf(randomTableName));
        ResultScanner scanner = resultTable.getScanner(scan);

        InstrumentPricesResponse response = buildResponse(scanner);

        scanner.close();
        resultTable.close();
        deleteTable(randomTableName);

        return response;
    }

    private InstrumentPricesResponse buildResponse(ResultScanner scanner) {
        InstrumentPricesResponse.Builder responseBuilder = InstrumentPricesResponse.newBuilder();
        for (Result result : scanner) {
            byte[] rowKeyBytes = result.getRow(); // Get the row key bytes
            long interval = Bytes.toLong(rowKeyBytes); // Convert row key bytes to long
            double averagePrice = Bytes.toDouble(result.getValue(RESULT_CF, RESULT_COLUMN_QUALIFIER));

            Tick tick = Tick.newBuilder()
                    .setTimestamp(Timestamp.newBuilder().setSeconds(interval/1000))
                    .setValue(averagePrice)
                    .build();
            responseBuilder.addTicks(tick);
        }
        return responseBuilder.build();
    }

    public static class PriceMapper extends TableMapper<LongWritable, DoubleWritable> {

        private final LongWritable interval = new LongWritable();
        private final DoubleWritable price = new DoubleWritable();

        @Override
        protected void map(ImmutableBytesWritable rowKey, Result result, Context context) throws IOException, InterruptedException {
            String rowKeyStr = Bytes.toString(rowKey.get());
            String[] parts = rowKeyStr.split("_");
            long timestamp = Long.parseLong(parts[1]);
            double priceValue = Bytes.toDouble(result.getValue(Bytes.toBytes("series"), Bytes.toBytes("val")));
            long intervalStart = timestamp - (timestamp % context.getConfiguration().getLong("interval", 60000)); // Default interval 1 minute
            interval.set(intervalStart);
            price.set(priceValue);
            context.write(interval, price);
        }
    }

    public static class PriceReducer extends TableReducer<LongWritable, DoubleWritable, ImmutableBytesWritable> {

        public static final byte[] CF = "cf".getBytes();
        public static final byte[] COUNT = "count".getBytes();

        @Override
        protected void reduce(LongWritable key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0.0;
            int count = 0;
            for (DoubleWritable value : values) {
                sum += value.get();
                count++;
            }
            double average = sum / count;
            Put put = new Put(Bytes.toBytes(key.toString()));
            put.addColumn(CF, COUNT, Bytes.toBytes(average));
            context.write(null, put);
        }
    }
}
