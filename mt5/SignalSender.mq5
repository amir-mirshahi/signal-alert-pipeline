//+------------------------------------------------------------------+
//|                                                 SignalSender.mq5 |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property version   "1.00"

void OnStart()
{
    string url = "http://127.0.0.1:8000/webhook?token=my_super_secret_token";
    
    datetime time = TimeCurrent();
    string signal_id = "mt5-live-" + IntegerToString(time);
    double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    // NEW: Use _Point for correct pip math. 1 Point = 0.00001 for EURUSD.
    // We will set a Stop Loss of 200 points (20 pips) and Target of 400 points (40 pips).
    double stop_level = current_price - (200 * _Point);
    double target_level = current_price + (400 * _Point);
    
    string json = StringFormat(
        "{\"schema\": \"1.0\", \"source\": \"MT5\", \"indicator_version\": \"1.0.0\", "
        "\"signal_id\": \"%s\", \"symbol\": \"%s\", \"timeframe\": \"1h\", "
        "\"bar_time\": \"2025-01-01T00:00:00Z\", \"type\": \"entry\", "
        "\"direction\": \"long\", \"entry\": %.5f, \"stop\": %.5f, \"target\": %.5f}",
        signal_id, _Symbol, current_price, stop_level, target_level
    );
    
    char data[];
    int len = StringLen(json);
    StringToCharArray(json, data, 0, len, CP_UTF8);
    ArrayResize(data, len); 
    
    char result[];
    string result_headers;
    string headers = "Content-Type: application/json\r\n";
    
    Print("Sending signal to Python server...");
    int res = WebRequest("POST", url, headers, 5000, data, result, result_headers);
    
    if(res == -1) Print("Error: ", GetLastError());
    else {
        Print("Server responded with status: ", res);
    }
}
//+------------------------------------------------------------------+