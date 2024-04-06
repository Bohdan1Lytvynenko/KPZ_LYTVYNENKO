import pandas as pd  # Імпорт бібліотеки pandas для роботи з даними
import ta  # Імпорт бібліотеки ta для технічного аналізу
import matplotlib.pyplot as plt  # Імпорт pyplot з matplotlib для візуалізації даних
from binance.client import Client  # Імпорт Client з binance для доступу до API Binance
from matplotlib.dates import DateFormatter  # Імпорт DateFormatter для форматування дат

# Завантаження даних
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 day ago UTC",
    end_str="now UTC"
)

# Створення DataFrame з отриманих даних
k_lines = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')  # Конвертація часу з мілісекунд
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)  # Конвертація цін у формат float

# Розрахунок індикаторів
k_lines['RSI'] = ta.momentum.RSIIndicator(k_lines['close']).rsi()  # Індекс відносної сили (RSI)
k_lines['CCI'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()  # Індекс товарного каналу (CCI)
k_lines['MACD'] = ta.trend.MACD(k_lines['close']).macd()  # Індикатор рухомої середньої конвергенції/дивергенції (MACD)
k_lines['ATR'] = ta.volatility.AverageTrueRange(k_lines['high'], k_lines['low'], k_lines['close']).average_true_range()  # Середній істинний діапазон (ATR)
k_lines['ADX'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()  # Індекс середнього напрямку руху (ADX)

# Створення колонок сигналів
for indicator in ['RSI', 'CCI', 'MACD', 'ATR', 'ADX']:
    k_lines[f'{indicator}_buy_signal'] = (k_lines[indicator] < 30) & (k_lines[indicator].shift() >= 30)  # Сигнали купівлі
    k_lines[f'{indicator}_sell_signal'] = (k_lines[indicator] > 70) & (k_lines[indicator].shift() <= 70)  # Сигнали продажу

# Візуалізація цін закриття та індикаторів з сигналами
fig, axs = plt.subplots(6, 1, figsize=(14, 10), sharex=True)  # Створення субплотів

# Візуалізація ціни закриття
axs[0].plot(k_lines['time'], k_lines['close'], label='Ціна закриття', color='purple')
axs[0].set_title('Ціна закриття')
axs[0].legend()

# Візуалізація індикаторів
for i, indicator in enumerate(['RSI', 'MACD', 'ATR', 'ADX', 'CCI']):
    axs[i+1].plot(k_lines['time'], k_lines[indicator], label=indicator, color='purple')
    axs[i+1].scatter(k_lines.loc[k_lines[f'{indicator}_buy_signal'], 'time'], k_lines.loc[k_lines[f'{indicator}_buy_signal'], indicator], marker='^', color='green', label='Сигнал купівлі')
    axs[i+1].scatter(k_lines.loc[k_lines[f'{indicator}_sell_signal'], 'time'], k_lines.loc[k_lines[f'{indicator}_sell_signal'], indicator], marker='v', color='red', label='Сигнал продажу')
    axs[i+1].set_title(indicator)
    axs[i+1].legend()

# Форматування дат на осях X
date_form = DateFormatter("%m-%d %H:%M")
for ax in axs:
    ax.xaxis.set_major_formatter(date_form)

plt.tight_layout()
plt.show()
