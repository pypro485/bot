import random
import pandas as pd
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from datetime import datetime
from alpaca_trade_api import REST

from timedelta import Timedelta
from finbert_utils import estimate_sentiment
from stocks import stocks
from lumibot.traders import Trader

API_KEY = "PKRIJZYYHEJ2XSGY0T9O"
API_SECRET = "NN6HerdYHnHWF8WG3QX0gS3EYph1dKZVZBLnPwtM"
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy):
    def initialize(self, cash_at_risk: float = .5):
        self.stock_pool = self.load_stock_pool()  # Load stock symbols from CSV
        self.symbol = random.choice(self.stock_pool)  # Initial random stock selection
        self.sleeptime = "15M"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def load_stock_pool(self):
        df = pd.read_csv('stocks.csv')  # Adjust the path to your CSV file
        return stocks

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)

        if last_price is None:
            
            return None, None, None

        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        try:
            news = self.api.get_news(symbol=self.symbol,
                                     start=three_days_prior,
                                     end=today)
            news = [ev.__dict__["_raw"]["headline"] for ev in news]
            probability, sentiment = estimate_sentiment(news)
            return probability, sentiment
        except Exception as e:
            print(f"Error fetching sentiment: {e}")
            return None, None

    def on_trading_iteration(self):
        self.symbol = random.choice(self.stock_pool)

        cash, last_price, quantity = self.position_sizing()
        if last_price is None:
            return  # Skip this iteration if no valid price

        probability, sentiment = self.get_sentiment()
        if probability is None:
            return  # Skip if sentiment calculation fails

        if cash > last_price:
            if sentiment == "positive" and probability > .700:
                if self.last_trade == "sell":
                    self.sell_all()

                # Round take-profit and stop-loss prices
                take_profit_price = round(last_price * 1.20, 2)
                stop_loss_price = round(last_price * 0.95, 2)

                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price
                )
                self.submit_order(order)
                self.last_trade = "buy"

            elif sentiment == "negative" and probability > .700:
                if self.last_trade == "buy":
                    self.sell_all()

                # Round take-profit and stop-loss prices
                take_profit_price = round(last_price * 0.80, 2)
                stop_loss_price = round(last_price * 1.05, 2)

                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price
                )
                self.submit_order(order)
                self.last_trade = "sell"

start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31) 
broker = Alpaca(ALPACA_CREDS) 
strategy = MLTrader(name='mlstrat', broker=broker, 
                    parameters={"symbol":"SPY", 
                                "cash_at_risk":.5}, should_send_summary_to_discord=True, discord_webhook_url='https://discord.com/api/webhooks/1284306717580070933/BBc5joYaRco4TJwVpoh8cwLtLQjRxVdQM8-ENlxA2etJryCNQqGIvHecj5nJkgypQ0pc', db_connection_str='sqlite:///C:/Users/somen/dbNAME.db')
# strategy.backtest(
#     YahooDataBacktesting, 
#     start_date, 
#     end_date, 
#     parameters={"symbol":"SPY", "cash_at_risk":.5},
#     thetadata_username="arnavchaturvedi5050@gmail.com",
#     thetadata_password="n!QxmW!y2rJURVc"
# )
trader = Trader()
trader.add_strategy(strategy)
trader.run_all()