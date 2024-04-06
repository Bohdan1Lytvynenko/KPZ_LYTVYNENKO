import pandas as pd  # Імпортування бібліотеки pandas для роботи з табличними даними
from datetime import datetime  # Імпортування класу datetime для роботи з датами та часом

# Перевірка наявності файлу і його читання, якщо він існує
try:
    df = pd.read_csv('filename.csv')  # Спроба відкрити файл для читання
except FileNotFoundError:  # Якщо файл не знайдено, то викликається цей блок
    df = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second'])  # Створення нового порожнього DataFrame

# Отримання поточної дати та часу
now = datetime.now()  # Запис поточної дати та часу в змінну now

# Додавання нового рядка з поточною датою і часом
df.loc[len(df)] = now.strftime('%Y %m %d %H %M %S').split()  # Форматування поточної дати та часу і додавання їх як новий рядок у DataFrame

# Збереження даних у файл
df.to_csv("filename.csv", index=False)  # Збереження DataFrame до файлу без індексу

print(df)  # Виведення DataFrame на екран
