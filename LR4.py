import pandas as pd  # Імпорт бібліотеки pandas для роботи з даними
import ta  # Імпорт бібліотеки ta для технічного аналізу
import matplotlib.pyplot as plt  # Імпорт pyplot з matplotlib для візуалізації даних
from binance import Client  # Імпорт Client з binance для доступу до API Binance
from matplotlib.dates import DateFormatter  # Імпорт DateFormatter для форматування дат

# Завантаження даних
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",  # Символ торгової пари
    interval=Client.KLINE_INTERVAL_1MINUTE,  # Інтервал часу між котируваннями
    start_str="1 day ago UTC",  # Початкова дата запиту
    end_str="now UTC"  # Кінцева дата запиту
)

# Створення DataFrame з отриманих даних
k_lines = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')  # Конвертація часу з мілісекунд
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)  # Конвертація цін у формат float

# Розрахунок індикаторів
periods = [14, 27, 100]  # Визначення періодів для розрахунку RSI
for period in periods:
    rsi_indicator = ta.momentum.RSIIndicator(k_lines['close'], window=period)  # Створення RSI індикатору для кожного періоду
    k_lines[f'RSI_{period}'] = rsi_indicator.rsi()  # Зберігання значень RSI в DataFrame

# Візуалізація цін закриття та індикаторів
plt.figure(figsize=(14, 10))  # Створення фігури для графіків
plt.subplot(4, 1, 1)  # Створення субплоту для ціни закриття
plt.plot(k_lines['time'], k_lines['close'], label='Ціна закриття')  # Візуалізація ціни закриття
plt.title('Ціна закриття')  # Заголовок графіку
plt.ylabel('Ціна')  # Підпис осі Y

# Цикл для візуалізації RSI для кожного періоду
for period in periods:
    plt.subplot(4, 1, periods.index(period) + 2)  # Створення субплоту для кожного RSI індикатору
    plt.plot(k_lines['time'], k_lines[f'RSI_{period}'], label=f'RSI_{period}', color='purple')  # Візуалізація RSI
    plt.title(f'RSI_{period}')  # Заголовок графіку
    plt.ylabel('RSI')  # Підпис осі Y
    plt.legend()  # Додавання легенди

# Форматування дат на осі X
date_form = DateFormatter("%m-%d %H:%M")  # Встановлення формату дати
plt.gca().xaxis.set_major_formatter(date_form)  # Застосування формату до поточного субплоту

plt.tight_layout()  # Автоматичне розміщення елементів всередині фігури
plt.show()  # Відображення графіків
