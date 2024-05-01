package hbaseclient;
import io.grpc.stub.StreamObserver;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.filter.CompareFilter;
import org.apache.hadoop.hbase.util.Bytes;
import org.json.JSONObject;
import proto.hbaseclient.*;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Random;

public class TradeExecutorService extends TradeExecutorGrpc.TradeExecutorImplBase{
    private final Table usersTable;
    private final Table portfolioTable;
    private final Table financialInstrumentsTable;
    private final Table popularityToInstrumentTable;
    private final String userInfoCF = "info";
    private final String balanceQualifier = "balance";
    private final String positionCF = "positions";
    private final String quantityQualifier = "quantity";
    private final String lockQualifier ="lock";
    private final String financialInstrumentInfoCF = "info";
    private final String popularityQualifier = "popularity";

    public TradeExecutorService(Table usersTable,Table portfolioTable,Table financialInstrumentsTable, Table popularityToInstrumentTable) {
        this.usersTable = usersTable;
        this.portfolioTable = portfolioTable;
        this.popularityToInstrumentTable = popularityToInstrumentTable;
        this.financialInstrumentsTable = financialInstrumentsTable;
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
        jsonTrade.put("type", trade.getType()==TradeType.BUY?"P":"S");
        jsonTrade.put("symbol", trade.getSymbol());
        jsonTrade.put("quantity", trade.getQuantity());
        jsonTrade.put("price_per_item", trade.getPricePerItem());
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

    public static long calculateTradeScore(Trade trade){
        long costOfTrade = (trade.getQuantity()*trade.getPricePerItem())/100;
        String myDate = "2020/01/01 00:00:00";
        LocalDateTime localDateTime = LocalDateTime.parse(myDate,
                DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss") );

        long millis2020 = localDateTime
                .atZone(ZoneId.systemDefault())
                .toInstant().toEpochMilli();

        long secondsSince2020 = trade.getTimeExecuted()/1000 - millis2020/1000;
        long x = (long) ((secondsSince2020) /(3600*24*30));
        return (long) ((costOfTrade * Math.pow(2, x)) / 1000000000);
    }

    private void updatePopularity(Trade trade) throws IOException{
        long tradeScore = calculateTradeScore(trade);
        long newReverseScore = financialInstrumentsTable.incrementColumnValue(
                Bytes.toBytes(trade.getUsername()),
                Bytes.toBytes(financialInstrumentInfoCF),
                Bytes.toBytes(popularityQualifier),
                -tradeScore
        );
        Get getFinancialInstrumentInfo = new Get(Bytes.toBytes(trade.getSymbol()));

        String nameQualifier = "name";
        String currencyQualifier = "currency";
        String imageQualifier = "image";
        getFinancialInstrumentInfo.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(nameQualifier));
        getFinancialInstrumentInfo.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(currencyQualifier));
        getFinancialInstrumentInfo.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(imageQualifier));

        Result financialInstrumentInfo = financialInstrumentsTable.get(getFinancialInstrumentInfo);
        byte[] nameBytes = financialInstrumentInfo.getValue(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(nameQualifier));
        byte[] currencyBytes = financialInstrumentInfo.getValue(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(currencyQualifier));
        byte[] imageBytes = financialInstrumentInfo.getValue(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(imageQualifier));
        
        long oldReverseScore = newReverseScore + tradeScore;
    

        String oldScoreKey = oldReverseScore+"_"+trade.getSymbol();
        String newScoreKey = newReverseScore+"_"+trade.getSymbol();
        Delete deleteOldScore = new Delete(Bytes.toBytes(oldScoreKey));
        Put createNewScore = new Put(Bytes.toBytes(newScoreKey));

        createNewScore.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(nameQualifier),nameBytes);
        createNewScore.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(currencyQualifier),currencyBytes);
        createNewScore.addColumn(Bytes.toBytes(financialInstrumentInfoCF), Bytes.toBytes(imageQualifier),imageBytes);

        popularityToInstrumentTable.delete(deleteOldScore);
        popularityToInstrumentTable.put(createNewScore);
    }

    private boolean updateUserPortfolioMoneyInvested(Trade trade) throws IOException{
        String portfolioRow = trade.getUsername() + "_" + trade.getSymbol();
        int SALT_LENGTH = 10;
        byte[] salt = new byte[SALT_LENGTH];
        new Random().nextBytes(salt);

        try {
            Increment moneyInvestedIncrement = new Increment(Bytes.toBytes(portfolioRow));
            RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
            if (this.lockPortfolioRow(trade,salt)) {
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
                updatePopularity(trade);
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
                }
                updatePopularity(trade);
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