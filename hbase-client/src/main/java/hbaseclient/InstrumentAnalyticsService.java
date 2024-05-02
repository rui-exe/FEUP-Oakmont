package hbaseclient;

import com.google.protobuf.Timestamp;
import io.grpc.stub.StreamObserver;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.CellUtil;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.io.ImmutableBytesWritable;
import org.apache.hadoop.hbase.mapreduce.TableMapReduceUtil;
import org.apache.hadoop.hbase.mapreduce.TableMapper;
import org.apache.hadoop.hbase.mapreduce.TableReducer;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.mapreduce.Job;
import org.bouncycastle.util.Arrays;

import proto.hbaseclient.InstrumentAnalyticsGrpc;
import proto.hbaseclient.InstrumentPricesRequest;
import proto.hbaseclient.InstrumentPricesResponse;
import proto.hbaseclient.Tick;

import java.io.IOException;
import java.util.UUID;

import java.nio.charset.StandardCharsets;


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


    private void createResultTable(String name) throws IOException {
        Admin admin = connection.getAdmin();
        TableDescriptorBuilder tableDescriptorBuilder = TableDescriptorBuilder.newBuilder(TableName.valueOf(name));
        ColumnFamilyDescriptor columnFamilyDescriptor = ColumnFamilyDescriptorBuilder.newBuilder(RESULT_CF).build();
        tableDescriptorBuilder.setColumnFamily(columnFamilyDescriptor);
        TableDescriptor tableDescriptor = tableDescriptorBuilder.build();
        admin.createTable(tableDescriptor);
        admin.close();
    }

    private void deleteResultTable(String name) throws IOException{
        Admin admin = connection.getAdmin();
        admin.disableTable(TableName.valueOf(name));
        admin.deleteTable(TableName.valueOf(name));
        admin.close();
    }

    public static byte[] combineBytes(byte[] array1, byte[] array2){
        int combinedLength = array1.length + array2.length;

        byte[] combinedArray = new byte[combinedLength];

        System.arraycopy(array1, 0, combinedArray, 0, array1.length);

        System.arraycopy(array2, 0, combinedArray, array1.length, array2.length);
        
        return combinedArray;
    }

    private InstrumentPricesResponse calculateAggregatedPrices(InstrumentPricesRequest request) throws IOException, InterruptedException, ClassNotFoundException {
        String randomTableName = "tmp_" + UUID.randomUUID().toString().replace("-", "");
        createResultTable(randomTableName);
        conf.setLong("delta", request.getTimeDelta().getSeconds()*1000);
        conf.setLong("start.date", request.getStartDate().getSeconds()*1000);

        Job job = Job.getInstance(conf, "CalculateInstrumentPrices");

        job.setJarByClass(InstrumentAnalyticsService.class);
        Scan scan = new Scan();

        byte[] startRow = combineBytes(
            Bytes.toBytes(request.getSymbol() + "_"),
            Bytes.toBytes(request.getStartDate().getSeconds() * 1000)
        );
        byte[] endRow = combineBytes(
            Bytes.toBytes(request.getSymbol() + "_"),
            Bytes.toBytes(request.getEndDate().getSeconds() * 1000)
        );

        scan.withStartRow(startRow);
        scan.withStopRow(endRow,true);

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

        scan = new Scan();
        Table resultTable = connection.getTable(TableName.valueOf(randomTableName));
        ResultScanner scanner = resultTable.getScanner(scan);
        InstrumentPricesResponse response = buildResponse(scanner);

        scanner.close();
        resultTable.close();
        deleteResultTable(randomTableName);

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
            byte underscoreByte = "_".getBytes(StandardCharsets.UTF_8)[0];
            int underscoreIndex = -1;
            for (int i = 0; i < rowKey.get().length; i++) {
                if (rowKey.get()[i] == underscoreByte) {
                    underscoreIndex = i;
                    break;
                }
            }

            if (underscoreIndex != -1 && underscoreIndex < rowKey.get().length - 1) {
                byte[] timestampBytes = Arrays.copyOfRange(rowKey.get(), underscoreIndex + 1, rowKey.get().length);
                long intervalStart = Bytes.toLong(timestampBytes);
                String priceValueStr = Bytes.toString(result.getValue(Bytes.toBytes("series"), Bytes.toBytes("val")));
                double priceValue = Double.parseDouble(priceValueStr);
                long delta = context.getConfiguration().getLong("delta", 24*60*60*1000); // Default interval 1 day
                long startDate = context.getConfiguration().getLong("start.date", 0); // Default is epoch start
                
                intervalStart -= startDate; //so start date aligns with the first beggining of the first aggregation bucket
                intervalStart -= (intervalStart%delta); 
                intervalStart += startDate; //add back start date
                
                interval.set(intervalStart);
                price.set(priceValue);
                context.write(interval, price);
            }
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
            Put put = new Put(Bytes.toBytes(key.get()));
            put.addColumn(CF, COUNT, Bytes.toBytes(average));
            context.write(null, put);
        }
    }
}
