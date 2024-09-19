# candlestick_patterns_backtest.py

from lumibot.strategies import Strategy
from lumibot.backtesting import YahooDataBacktesting
import yfinance as yf
import pandas as pd
from lumibot.brokers import Alpaca
# Alpaca credentials and configuration
ALPACA_CREDS = {
    "API_KEY": "PKRIJZYYHEJ2XSGY0T9O",
    "API_SECRET": "NN6HerdYHnHWF8WG3QX0gS3EYph1dKZVZBLnPwtM",
    "PAPER": True
}

class CandlestickPatternsStrategy(Strategy):
    def initialize(self):
        self.stock_symbol = "AAPL"  # Example stock symbol
        self.cash_at_risk = 0.5
        self.data = yf.download(self.stock_symbol, period="1y", interval="5m")
        self.data = self.data.reset_index()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.broker = Alpaca(ALPACA_CREDS) 
    def handle_data(self, data):
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df = df.reset_index()

        if len(df) < 3:
            return

        # Extract the last three candles
        last_candles = df.tail(3)

        if self.bullish_engulfing(last_candles):
            self.log(f"Bullish Engulfing pattern found!")
        elif self.bearish_engulfing(last_candles):
            self.log(f"Bearish Engulfing pattern found!")

    def bullish_engulfing(self, candles):
        # Logic for Bullish Engulfing
        first_candle = candles.iloc[0]
        second_candle = candles.iloc[1]
        third_candle = candles.iloc[2]

        return (first_candle['Close'] < first_candle['Open'] and
                second_candle['Close'] < second_candle['Open'] and
                third_candle['Close'] > third_candle['Open'] and
                third_candle['Close'] > first_candle['High'] and
                third_candle['Open'] < first_candle['Low'])

    def bearish_engulfing(self, candles):
        # Logic for Bearish Engulfing
        first_candle = candles.iloc[0]
        second_candle = candles.iloc[1]
        third_candle = candles.iloc[2]

        return (first_candle['Close'] > first_candle['Open'] and
                second_candle['Close'] > second_candle['Open'] and
                third_candle['Close'] < third_candle['Open'] and
                third_candle['Close'] < first_candle['Low'] and
                third_candle['Open'] > first_candle['High'])

def run_backtest():
    # Initialize strategy
    strategy = CandlestickPatternsStrategy()
    
    # Define parameters for the backtest
    parameters = {
        "symbol": "AAPL",
        "cash_at_risk": 0.5
    }
    broker = Alpaca(ALPACA_CREDS) 

    # Initialize and run the backtest
    backtest = YahooDataBacktesting(
        strategy=strategy,
        start_date="2023-01-01",
        end_date="2023-12-31",
        parameters=parameters,
        broker=broker
    )
    
    # Run backtest and print results
    results = backtest.run()
    print(results)

if __name__ == "__main__":
    run_backtest()
