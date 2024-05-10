import pandas as pd
from binance import Client
from dataclasses import dataclass
from typing import List
import ta

@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float = None
    closed_by: str = None

def get_data(client, symbol: str, interval: str, start_str: str, end_str: str):
    k_lines = client.get_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(k_lines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].astype(float)
    return df

def add_indicators(df):
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
    df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
    return df

def generate_signals(df):
    signals = []
    for i, row in df.iterrows():
        if row['cci'] < -100 and row['adx'] > 25:
            signal_type = 'sell'
        elif row['cci'] > 100 and row['adx'] > 25:
            signal_type = 'buy'
        else:
            continue

        stop_loss = round(row['close'] * (1 + 0.01 if signal_type == 'sell' else 1 - 0.01), 2)
        take_profit = round(row['close'] * (1 - 0.015 if signal_type == 'sell' else 1 + 0.015), 2)

        signals.append(Signal(row['time'], 'BTCUSDT', 100, signal_type, row['close'], take_profit, stop_loss))
    return signals

def backtest_signals(df, signals):
    results = []
    for signal in signals:
        data_slice = df[df['time'] >= signal.time]
        for index, row in data_slice.iterrows():
            if signal.side == 'sell' and row['low'] <= signal.take_profit or \
               signal.side == 'buy' and row['high'] >= signal.take_profit:
                signal.result = signal.take_profit - signal.entry if signal.side == 'buy' else signal.entry - signal.take_profit
                signal.closed_by = "TP"
                break
            elif signal.side == 'sell' and row['high'] >= signal.stop_loss or \
                 signal.side == 'buy' and row['low'] <= signal.stop_loss:
                signal.result = signal.stop_loss - signal.entry if signal.side == 'buy' else signal.entry - signal.stop_loss
                signal.closed_by = "SL"
                break
        if signal.result is not None:
            results.append(signal)
    return results

def calculate_statistics(trades):
    total_pnl = sum(trade.result for trade in trades)
    total_profit = sum(trade.result for trade in trades if trade.result > 0)
    total_loss = sum(trade.result for trade in trades if trade.result < 0)
    profit_factor = total_profit / abs(total_loss) if total_loss != 0 else float('inf')
    print(f"Total PnL: {total_pnl}, Profit Factor: {profit_factor}")

# Example usage:
client = Client()
df = get_data(client, "BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 week ago UTC", "now UTC")
df = add_indicators(df)
signals = generate_signals(df)
results = backtest_signals(df, signals)
for result in results:
    print(result)
calculate_statistics(results)
