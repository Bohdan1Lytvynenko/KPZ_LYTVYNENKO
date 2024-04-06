import pandas as pd  # Імпорт бібліотеки pandas для роботи з даними
import ta  # Імпорт бібліотеки ta для технічного аналізу
from matplotlib import pyplot as plt  # Імпорт pyplot для візуалізації даних
from binance import Client  # Імпорт Client для доступу до API Binance
from dataclasses import dataclass  # Імпорт dataclass для створення класу сигналів

@dataclass
class Signal:
    time: pd.Timestamp  # Час сигналу
    asset: str  # Актив
    quantity: float  # Кількість для торгівлі
    side: str  # Сторона (купівля чи продаж)
    entry: float  # Ціна входу
    take_profit: float  # Ціна для взяття прибутку
    stop_loss: float  # Ціна стоп-збитку
    result: float  # Результат торгівлі (поки не використовується)

def create_signals(k_lines):
    signals = []
    for i in range(len(k_lines)):
        signal = "No signal"
        # Задайте значення за замовчуванням для цих змінних
        take_profit_price = None
        stop_loss_price = None
        current_price = k_lines.iloc[i]['close']
        if k_lines.iloc[i]['cci'] < -100 and k_lines.iloc[i]['adx'] > 25:
            signal = 'sell'
        elif k_lines.iloc[i]['cci'] > 100 and k_lines.iloc[i]['adx'] > 25:
            signal = 'buy'

        if signal == "buy":
            stop_loss_price = round((1 - 0.02) * current_price, 1)
            take_profit_price = round((1 + 0.1) * current_price, 1)
        elif signal == "sell":
            stop_loss_price = round((1 + 0.02) * current_price, 1)
            take_profit_price = round((1 - 0.1) * current_price, 1)

        # Тепер змінні take_profit_price та stop_loss_price будуть мати значення None,
        # якщо жодна з умов для "buy" або "sell" не виконується
        signals.append(Signal(
            k_lines.iloc[i]['time'],
            'BTCUSDT',
            100,
            signal,
            current_price,
            take_profit_price,
            stop_loss_price,
            None
        ))
    return signals


# Підключення до API Binance і завантаження даних
client = Client()
k_lines = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 week ago UTC",
    end_str="now UTC"
)

# Перетворення даних у DataFrame
k_lines = pd.DataFrame(k_lines,
                       columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                                'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)

# Обчислення індикаторів ADX і CCI
k_lines['adx'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()
k_lines['cci'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()

# Генерація сигналів
signals = create_signals(k_lines)

# Візуалізація ціни закриття та сигналів
plt.figure(figsize=(12, 6))
plt.plot(k_lines['time'], k_lines['close'], label='Ціна BTCUSDT')

for signal in signals:
    if signal.side == 'buy':
        plt.scatter(signal.time, signal.entry, color='green', label='Сигнал купівлі', marker='^', s=100)
    elif signal.side == 'sell':
        plt.scatter(signal.time, signal.entry, color='red', label='Сигнал продажу', marker='v', s=100)

plt.title('Ціна BTCUSDT і сигнали')
plt.xlabel('Час')
plt.ylabel('Ціна')
plt.legend()
plt.grid(True)
plt.show()
