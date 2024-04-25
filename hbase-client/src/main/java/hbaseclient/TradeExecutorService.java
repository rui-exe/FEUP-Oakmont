package hbaseclient;
import io.grpc.stub.StreamObserver;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.filter.CompareFilter;
import org.apache.hadoop.hbase.util.Bytes;
import org.json.JSONObject;
import proto.hbaseclient.*;

import java.io.IOException;
import java.util.Random;

public class TradeExecutorService extends TradeExecutorGrpc.TradeExecutorImplBase{
    private final Table usersTable;
    private final Table portfolioTable;
    private final String userInfoCF = "info";
    private final String balanceQualifier = "balance";
    private final String positionCF = "positions";
    private final String quantityQualifier = "quantity";
    private final String lockQualifier ="lock";


    public TradeExecutorService(Table usersTable,Table portfolioTable) {
        this.usersTable = usersTable;
        this.portfolioTable = portfolioTable;
    }

    private boolean lockPortfolioRow(Trade trade,byte[] salt) throws IOException {
        long LOCK_TTL_SECONDS = 5;
        long lockTTL = LOCK_TTL_SECONDS *1000;

        String portfolioRow = trade.getUsername() + "_" + trade.getSymbol();

        Put lockRow = new Put(Bytes.toBytes(portfolioRow));
        lockRow.addColumn(
                Bytes.toBytes(this.positionCF),
                Bytes.toBytes(this.lockQualifier),
                salt
        );
        lockRow.setTTL(lockTTL);

        RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
        mutations.add(lockRow);

        return this.portfolioTable.checkAndMutate(
                Bytes.toBytes(portfolioRow), Bytes.toBytes(this.positionCF), Bytes.toBytes(this.lockQualifier),
                CompareFilter.CompareOp.EQUAL,
                null,
                mutations
        );
    }

    private boolean mutateAndUnlockPortfolioRow(Trade trade, byte[] salt, RowMutations mutations) throws IOException{
        String portfolioRow = trade.getUsername() + "_" + trade.getSymbol();

        Delete unlockRow = new Delete(Bytes.toBytes(portfolioRow));
        unlockRow.addColumn(
                Bytes.toBytes(this.positionCF),
                Bytes.toBytes(this.lockQualifier)
        );
        mutations.add(unlockRow);

        return this.portfolioTable.checkAndMutate(
                Bytes.toBytes(portfolioRow), Bytes.toBytes(this.positionCF), Bytes.toBytes(this.lockQualifier),
                CompareFilter.CompareOp.EQUAL,
                salt,
                mutations
        );
    }

    private static JSONObject tradeToJson(Trade trade){
        JSONObject jsonTrade = new JSONObject();
        jsonTrade.put("type", trade.getType().name());
        jsonTrade.put("symbol", trade.getSymbol());
        jsonTrade.put("quantity", trade.getQuantity());
        jsonTrade.put("price_per_item", trade.getSymbol());
        jsonTrade.put("time_offered", trade.getTimeOffered());
        return jsonTrade;
    }

    private RowMutations updateUserBalanceAndTrades(Trade trade) throws IOException{
        String username = trade.getUsername();
        JSONObject jsonTrade = tradeToJson(trade);
        String jsonString = jsonTrade.toString();
        long totalPrice = trade.getQuantity()*trade.getPricePerItem();
        Append tradeAppend = new Append(Bytes.toBytes(username));
        String userTradesCF = "trades";
        tradeAppend.addColumn(
                Bytes.toBytes(userTradesCF),
                Bytes.toBytes(Long.MAX_VALUE-trade.getTimeExecuted()),
                Bytes.toBytes(jsonString)
        );

        Increment balanceIncrement = new Increment(Bytes.toBytes(username));
        if(trade.getType()==TradeType.BUY)
            balanceIncrement.addColumn(Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier), -totalPrice);
        else
            balanceIncrement.addColumn(Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier), totalPrice);

        RowMutations mutations = new RowMutations(Bytes.toBytes(username));
        mutations.add(balanceIncrement);
        mutations.add(tradeAppend);
        return mutations;
    }

    private RowMutations updateUserPortfolioQuantity(Trade trade) throws IOException{
        String portfolioRow = trade.getUsername()+"_"+trade.getSymbol();
        Increment quantityIncrement = new Increment(Bytes.toBytes(portfolioRow));
        if(trade.getType()==TradeType.BUY){
            quantityIncrement.addColumn(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier), trade.getQuantity());
        }
        else{
            quantityIncrement.addColumn(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier), -trade.getQuantity());
        }
        RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
        mutations.add(quantityIncrement);
        return mutations;
    }


    private boolean updateUserPortfolioMoneyInvested(Trade trade) throws IOException{
        String portfolioRow = trade.getUsername() + "_" + trade.getSymbol();
        boolean lockAcquired = false;
        int SALT_LENGTH = 10;
        byte[] salt = new byte[SALT_LENGTH];
        new Random().nextBytes(salt);
        try {
            Increment moneyInvestedIncrement = new Increment(Bytes.toBytes(portfolioRow));
            RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
            if (this.lockPortfolioRow(trade,salt)) {
                lockAcquired = true;
                String moneyInvestedQualifier = "money_invested";
                if (trade.getType() == TradeType.BUY) {
                    moneyInvestedIncrement.addColumn(
                            Bytes.toBytes(this.positionCF),
                            Bytes.toBytes(moneyInvestedQualifier),
                            trade.getQuantity()*trade.getPricePerItem()
                    );
                } else {
                    Get getPortfolioData = new Get(Bytes.toBytes(portfolioRow));
                    Result portfolioResult = portfolioTable.get(getPortfolioData);
                    byte[] quantityBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier));
                    byte[] moneyInvestedBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(moneyInvestedQualifier));

                    if(quantityBytes==null || moneyInvestedBytes==null)
                        return false;

                    long portfolioQuantity = Bytes.toLong(quantityBytes);
                    long portfolioMoneyInvested = Bytes.toLong(moneyInvestedBytes);

                    //portfolio quantity was already decreased by the ammount which was sold
                    //need to add that quantity so that it is taken into account
                    long averagePricePerStock = portfolioMoneyInvested / (portfolioQuantity+trade.getQuantity());

                    long amountToSubtract = trade.getQuantity() * averagePricePerStock;

                    moneyInvestedIncrement.addColumn(
                            Bytes.toBytes(this.positionCF),
                            Bytes.toBytes(moneyInvestedQualifier),
                            -amountToSubtract
                    );
                }
                mutations.add(moneyInvestedIncrement);
                return this.mutateAndUnlockPortfolioRow(trade, salt, mutations);
            }
            else
                return false;
        }
        catch (IOException e){
            this.mutateAndUnlockPortfolioRow(trade, salt, new RowMutations(Bytes.toBytes(portfolioRow)));
            return false;
        }
    }


    @Override
    public void executeBuyTrade(Trade trade, StreamObserver<TradeResult> responseObserver) {
        TradeResult result;

        if (trade.getType() != TradeType.BUY) {
            result = TradeResult.newBuilder()
                    .setResult(TradeResultType.WRONG_TRADE_TYPE)
                    .build();
            responseObserver.onNext(result);
            responseObserver.onCompleted();
            return;
        }
        try {
            RowMutations userMutations = updateUserBalanceAndTrades(trade);
            boolean transactionWentThrough = this.usersTable.checkAndMutate(
                    Bytes.toBytes(trade.getUsername()), Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier),
                    CompareFilter.CompareOp.LESS_OR_EQUAL,
                    Bytes.toBytes(trade.getQuantity()*trade.getPricePerItem()),
                    userMutations);

            if (transactionWentThrough) {
                RowMutations incrementPortfolioQuantity = updateUserPortfolioQuantity(trade);
                this.portfolioTable.mutateRow(incrementPortfolioQuantity);
                while (!this.updateUserPortfolioMoneyInvested(trade)) {
                }
                ;
                result = TradeResult.newBuilder()
                        .setResult(TradeResultType.TRADE_EXECUTED_SUCCESFULLY)
                        .build();
                responseObserver.onNext(result);
                responseObserver.onCompleted();

            } else {
                result = TradeResult.newBuilder()
                        .setResult(TradeResultType.NOT_ENOUGH)
                        .build();
                responseObserver.onNext(result);
                responseObserver.onCompleted();
           }
        }
        catch (IOException e) {
            result = TradeResult.newBuilder()
                    .setResult(TradeResultType.UNEXPECTED_SERVER_ERROR)
                    .build();
            responseObserver.onNext(result);
            responseObserver.onCompleted();
        }

    }

    @Override
    public void executeSellTrade(Trade trade, StreamObserver<TradeResult> responseObserver) {
        TradeResult result;

        if (trade.getType() != TradeType.SELL){
            result = TradeResult.newBuilder()
                    .setResult(TradeResultType.WRONG_TRADE_TYPE)
                    .build();
            responseObserver.onNext(result);
            responseObserver.onCompleted();
            return;
        }
        try {
            RowMutations decrementPortfolioQuantity = updateUserPortfolioQuantity(trade);
            String portfolioRow = trade.getUsername()+"_"+trade.getSymbol();

            boolean transactionWentThrough = this.portfolioTable.checkAndMutate(
                    Bytes.toBytes(portfolioRow), Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier),
                    CompareFilter.CompareOp.LESS_OR_EQUAL,
                    Bytes.toBytes(trade.getQuantity()),
                    decrementPortfolioQuantity);

            if (transactionWentThrough) {
                RowMutations userMutations = updateUserBalanceAndTrades(trade);
                this.usersTable.mutateRow(userMutations);
                while(!this.updateUserPortfolioMoneyInvested(trade)){
                };
                result = TradeResult.newBuilder()
                        .setResult(TradeResultType.TRADE_EXECUTED_SUCCESFULLY)
                        .build();
                responseObserver.onNext(result);
                responseObserver.onCompleted();
            }
            else {
                result = TradeResult.newBuilder()
                        .setResult(TradeResultType.NOT_ENOUGH)
                        .build();
                responseObserver.onNext(result);
                responseObserver.onCompleted();
            }
        }
        catch (IOException e) {
            result = TradeResult.newBuilder()
                    .setResult(TradeResultType.UNEXPECTED_SERVER_ERROR)
                    .build();
            responseObserver.onNext(result);
            responseObserver.onCompleted();
        }
    }
}