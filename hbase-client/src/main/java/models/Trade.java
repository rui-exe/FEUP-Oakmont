package models;
import org.json.JSONObject;

public class Trade {
    public enum TradeType {
        BUY,
        SELL
    }

    private String username;
    private TradeType type;
    private String symbol;
    private long quantity;
    private long pricePerItem;
    private long timeOffered;
    private long timeExecuted;

    public Trade(String username,TradeType type, String symbol, long quantity, long pricePerItem, long timeOffered, long timeExecuted) {
        this.username = username;
        this.type = type;
        this.symbol = symbol;
        this.quantity = quantity;
        this.pricePerItem = pricePerItem;
        this.timeOffered = timeOffered;
        this.timeExecuted = timeExecuted;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public TradeType getType() {
        return type;
    }

    public void setType(TradeType type) {
        this.type = type;
    }

    public String getSymbol() {
        return symbol;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public long getQuantity() {
        return quantity;
    }

    public void setQuantity(long quantity) {
        this.quantity = quantity;
    }

    public long getPricePerItem() {
        return pricePerItem;
    }

    public void setPricePerItem(long pricePerItem) {
        this.pricePerItem = pricePerItem;
    }

    public long getTimeOffered() {
        return timeOffered;
    }

    public void setTimeOffered(long timeOffered) {
        this.timeOffered = timeOffered;
    }

    public long getTimeExecuted() {
        return timeExecuted;
    }

    public void setTimeExecuted(long timeExecuted) {
        this.timeExecuted = timeExecuted;
    }

    public long getTotalPrice(){
        return this.quantity*this.pricePerItem;
    }


    public JSONObject toJSON() {
        JSONObject jsonTrade = new JSONObject();
        jsonTrade.put("type", type.name());
        jsonTrade.put("symbol", symbol);
        jsonTrade.put("quantity", quantity);
        jsonTrade.put("price_per_item", pricePerItem);
        jsonTrade.put("time_offered", timeOffered);
        return jsonTrade;
    }
}
