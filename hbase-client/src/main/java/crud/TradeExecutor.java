package crud;

import models.Trade;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.filter.CompareFilter;
import org.apache.hadoop.hbase.util.Bytes;
import org.json.JSONObject;

import java.io.IOException;
import java.time.ZonedDateTime;

import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.CellUtil;

import java.util.Random;


public class TradeExecutor {
    private Table usersTable;
    private Table portfolioTable;
    private String userTradesCF;
    private String userInfoCF;
    private String balanceQualifier;
    private String positionCF;
    private String quantityQualifier;
    private String moneyInvestedQualifier;
    private String lockQualifier;
    private long LOCK_TTL_SECONDS;
    private int SALT_LENGTH;

    public TradeExecutor(Table usersTable,Table portfolioTable) {
        this.usersTable = usersTable;
        this.portfolioTable = portfolioTable;
        this.userTradesCF = "trades";
        this.userInfoCF = "info";
        this.balanceQualifier = "balance";
        this.positionCF = "positions";
        this.quantityQualifier = "quantity";
        this.moneyInvestedQualifier = "money_invested";
        this.lockQualifier = "lock";
        this.LOCK_TTL_SECONDS = 5;
        this.SALT_LENGTH = 10;
    }

    public boolean lockPortfolioRow(Trade trade,byte[] salt) throws IOException{
        long lockTTL = this.LOCK_TTL_SECONDS*1000;

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

    public boolean mutateAndUnlockPortfolioRow(Trade trade, byte[] salt, RowMutations mutations) throws IOException{
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


    public RowMutations updateUserBalanceAndTrades(Trade trade) throws IOException{
        String username = trade.getUsername();
        JSONObject jsonTrade = trade.toJSON();
        String jsonString = jsonTrade.toString();
        long totalPrice = trade.getTotalPrice();
        Append tradeAppend = new Append(Bytes.toBytes(username));
        tradeAppend.addColumn(
                Bytes.toBytes(userTradesCF),
                Bytes.toBytes(Long.MAX_VALUE-trade.getTimeExecuted()), 
                Bytes.toBytes(jsonString)
        );

        Increment balanceIncrement = new Increment(Bytes.toBytes(username));
        if(trade.getType()==Trade.TradeType.BUY)
            balanceIncrement.addColumn(Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier), -totalPrice);
        else
            balanceIncrement.addColumn(Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier), totalPrice);
        
        RowMutations mutations = new RowMutations(Bytes.toBytes(username));
        mutations.add(balanceIncrement);
        mutations.add(tradeAppend);
        return mutations;
    }

    public RowMutations updateUserPortfolioQuantity(Trade trade) throws IOException{
        String portfolioRow = trade.getUsername()+"_"+trade.getSymbol();
        Increment quantityIncrement = new Increment(Bytes.toBytes(portfolioRow));
        if(trade.getType()==Trade.TradeType.BUY){
            quantityIncrement.addColumn(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier), trade.getQuantity());
        }
        else{
            quantityIncrement.addColumn(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier), -trade.getQuantity());
        }
        RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
        mutations.add(quantityIncrement);
        return mutations;
    }


    public boolean updateUserPortfolioMoneyInvested(Trade trade) throws IOException{
        String portfolioRow = trade.getUsername() + "_" + trade.getSymbol();
        boolean lockAcquired = false;
        byte[] salt = new byte[this.SALT_LENGTH];
        new Random().nextBytes(salt);
        try {
            Increment moneyInvestedIncrement = new Increment(Bytes.toBytes(portfolioRow));
            RowMutations mutations = new RowMutations(Bytes.toBytes(portfolioRow));
            if (this.lockPortfolioRow(trade,salt)) {
                lockAcquired = true;
                if (trade.getType() == Trade.TradeType.BUY) {
                    moneyInvestedIncrement.addColumn(
                            Bytes.toBytes(this.positionCF),
                            Bytes.toBytes(this.moneyInvestedQualifier),
                            trade.getTotalPrice()
                    );
                } else {
                    Get getPortfolioData = new Get(Bytes.toBytes(portfolioRow));
                    Result portfolioResult = portfolioTable.get(getPortfolioData);
                    byte[] quantityBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier));
                    byte[] moneyInvestedBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.moneyInvestedQualifier));
                    
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
                        Bytes.toBytes(this.moneyInvestedQualifier),
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

    public boolean executeBuyTrade(Trade trade) throws IOException {
        if (trade.getType() != Trade.TradeType.BUY)
            return false;
        
        RowMutations userMutations = updateUserBalanceAndTrades(trade);
        boolean transactionWentThrough = this.usersTable.checkAndMutate(
                Bytes.toBytes(trade.getUsername()), Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier),
                CompareFilter.CompareOp.LESS_OR_EQUAL,
                Bytes.toBytes(trade.getTotalPrice()),
                userMutations);

        if (transactionWentThrough) {
            RowMutations incrementPortfolioQuantity = updateUserPortfolioQuantity(trade);
            this.portfolioTable.mutateRow(incrementPortfolioQuantity);
            while(!this.updateUserPortfolioMoneyInvested(trade)){
            };
            return true;
        } else {
            return false;
        }
    }
    public boolean executeSellTrade(Trade trade) throws IOException {
        if (trade.getType() != Trade.TradeType.SELL)
            return false;

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
            return true;
        } else {
            return false;
        }
    }
    public void printUserDetails(String username) throws IOException {
        // Print user balance
        Get getUserDetails = new Get(Bytes.toBytes(username));
        Result userResult = usersTable.get(getUserDetails);
        
        byte[] balanceBytes = userResult.getValue(Bytes.toBytes(this.userInfoCF), Bytes.toBytes(this.balanceQualifier));
        if (balanceBytes != null) {
            long balance = Bytes.toLong(balanceBytes);
            System.out.println("Balance: " + balance);
        }
    
        // Print user trades
        System.out.println("\nUser Trades:");
        for (Cell tradeCell : userResult.rawCells()) {
            if (Bytes.toString(CellUtil.cloneFamily(tradeCell)).equals(this.userTradesCF)) {
                String tradeString = Bytes.toString(CellUtil.cloneValue(tradeCell));
                System.out.println(tradeString);
            }
        }    
    
        // Print user portfolio
        System.out.println("\nUser Portfolio:");
        Scan portfolioScan = new Scan().setRowPrefixFilter(Bytes.toBytes(username));
        ResultScanner portfolioScanner = portfolioTable.getScanner(portfolioScan);
        for (Result portfolioResult : portfolioScanner) {
            byte[] symbolBytes = portfolioResult.getRow();
            byte[] quantityBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.quantityQualifier));
            byte[] moneyInvestedBytes = portfolioResult.getValue(Bytes.toBytes(this.positionCF), Bytes.toBytes(this.moneyInvestedQualifier));
            if (symbolBytes != null && quantityBytes != null && moneyInvestedBytes != null) {
                String symbol = Bytes.toString(symbolBytes).split("_")[1];
                long quantity = Bytes.toLong(quantityBytes);
                long moneyInvested = Bytes.toLong(moneyInvestedBytes);
                System.out.println("Symbol: " + symbol + ", Quantity: " + quantity + ", Money Invested: " + moneyInvested);
            }
        }
    }
}
