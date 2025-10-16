import psycopg2
import random
import time
from config import DB_CONFIG

print("Выбери таблицу для вставки данных:")
print("1 - order_products_train")
print("2 - order_products_prior")

choice = input("Твой выбор (1/2): ").strip()
if choice == "1":
    TARGET_TABLE = "order_products_train"
elif choice == "2":
    TARGET_TABLE = "order_products_prior"
else:
    print("Неверный выбор. По умолчанию используем order_products_train.")
    TARGET_TABLE = "order_products_train"

try:
    interval = int(input("Введите интервал вставки (в секундах): ").strip())
    if interval <= 0:
        raise ValueError
except ValueError:
    print("Некорректное значение, ставим паузу по умолчанию = 20 сек.")
    interval = 20

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

print(f"✅ Соединение установлено. Будем вставлять данные в {TARGET_TABLE} каждые {interval} секунд...")

while True:
    # случайный пользователь и продукт
    cur.execute("SELECT user_id FROM orders ORDER BY random() LIMIT 1;")
    user_id = cur.fetchone()[0]

    cur.execute("SELECT product_id FROM products ORDER BY random() LIMIT 1;")
    product_id = cur.fetchone()[0]

    # новый order_id
    cur.execute("SELECT COALESCE(MAX(order_id), 0) + 1 FROM orders;")
    new_order_id = cur.fetchone()[0]

    # вставка заказа
    cur.execute("""
        INSERT INTO orders (order_id, user_id, eval_set, order_number, order_dow, order_hour_of_day, days_since_prior_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        new_order_id,
        user_id,
        'NEW',
        random.randint(1, 100),
        random.randint(0, 6),
        random.randint(0, 23),
        random.randint(1, 30)
    ))

    # вставка продукта в выбранную таблицу
    cur.execute(f"""
        INSERT INTO {TARGET_TABLE} (order_id, product_id, add_to_cart_order, reordered)
        VALUES (%s, %s, %s, %s)
    """, (
        new_order_id,
        product_id,
        1,
        random.randint(0, 1)
    ))

    print(f"[{TARGET_TABLE}] ➕ Добавлен заказ: order_id={new_order_id}, user_id={user_id}, product_id={product_id}")

    time.sleep(interval)