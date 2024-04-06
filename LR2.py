import pandas as pd  # Імпорт бібліотеки pandas для роботи з даними у формі таблиць
from binance.client import Client  # Імпорт класу Client для доступу до API біржі Binance

def calculate_rsi(prices, period):
    # Розрахунок індексу відносної сили (RSI)
    deltas = prices.diff()  # Визначення різниці між послідовними цінами
    gains = deltas.where(deltas > 0, 0)  # Виділення тільки позитивних змін
    losses = -deltas.where(deltas < 0, 0)  # Виділення тільки негативних змін
    avg_gain = gains.rolling(window=period, min_periods=1).mean()  # Обчислення середнього приросту за період
    avg_loss = losses.rolling(window=period, min_periods=1).mean()  # Обчислення середнього зниження за період
    rs = avg_gain / avg_loss  # Відношення середнього приросту до середнього зниження
    rsi = 100 - (100 / (1 + rs))  # Формула RSI
    return rsi

def get_rsi_data(asset, periods):
    # Отримання даних RSI для вказаного активу і періодів
    client = Client()  # Створення екземпляра клієнта API
    klines = client.get_historical_klines(
        symbol=asset,  # Символ активу, для якого збираються дані
        interval=Client.KLINE_INTERVAL_1MINUTE,  # Використання однієї хвилини як інтервалу між котируваннями
        start_str="1 day ago UTC",  # Запит даних за останній день
        end_str="now UTC"  # До поточного моменту
    )
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])  # Створення DataFrame з отриманих даних
    df['time'] = pd.to_datetime(df['time'], unit='ms')  # Конвертація часу з мілісекунд в зрозумілий формат
    df['close'] = df['close'].astype(float)  # Зміна типу даних цін закриття на float

    result = pd.DataFrame({'time': df['time']})  # Створення нової таблиці для результатів
    for period in periods:  # Для кожного з заданих періодів
        rsi_values = calculate_rsi(df['close'], period)  # Розрахунок RSI
        result[f'RSI_{period}'] = rsi_values  # Додавання значень RSI до таблиці результатів

    return result  # Повернення таблиці з результатами

asset = "BTCUSDT"  # Вказівка активу для аналізу
periods = [14, 27, 100]  # Визначення періодів для розрахунку RSI
rsi_data = get_rsi_data(asset, periods)  # Отримання RSI для вказаних періодів
print(rsi_data)  # Виведення результатів
