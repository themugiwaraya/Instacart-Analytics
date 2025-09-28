import psycopg2
import pandas as pd
import plotly.express as px
from config import DB_CONFIG
from analytics import load_queries

def run_time_slider():
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Успешное подключение к базе данных")

    queries = load_queries("queries.sql")
    if "query_11" not in queries:
        raise ValueError("❌ В queries.sql нет query_11 для временного ползунка")

    df = pd.read_sql(queries["query_11"], conn)
    conn.close()
    print(f"📊 Получено строк: {len(df)}")

    # --- Перевод дней недели и формат часов ---
    dow_map = {
        0: "Воскресенье",
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота"
    }
    df["order_dow"] = df["order_dow"].map(dow_map)

    # формат часов "HH:00"
    df["order_hour_str"] = df["order_hour_of_day"].astype(int).apply(lambda x: f"{x:02d}:00")

    # --- Задаём желаемый порядок ---
    dow_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    hours = [f"{h:02d}:00" for h in range(24)]

    # делаем категориальные колонки с явным порядком
    df["order_dow"] = pd.Categorical(df["order_dow"], categories=dow_order, ordered=True)
    df["order_hour_str"] = pd.Categorical(df["order_hour_str"], categories=hours, ordered=True)

    # --- Агрегация реальных данных ---
    counts = df.groupby(["order_dow", "order_hour_str"]).size().reset_index(name="total_orders")

    # --- Создаём полный grid (все дни × все часы) и заполняем отсутствующие нулями ---
    idx = pd.MultiIndex.from_product([dow_order, hours], names=["order_dow", "order_hour_str"])
    full = counts.set_index(["order_dow", "order_hour_str"]).reindex(idx, fill_value=0).reset_index()

    # --- Построение интерактивного графика ---
    fig = px.bar(
        full,
        x="order_hour_str",
        y="total_orders",
        animation_frame="order_dow",
        category_orders={"order_dow": dow_order, "order_hour_str": hours},
        labels={"order_hour_str": "Час заказа", "total_orders": "Количество заказов", "order_dow": "День недели"},
        title="📊 Количество заказов по часам (ползунок — день недели)"
    )

    # Слегка настроим внешний вид
    fig.update_layout(
        xaxis_tickangle=0,
        xaxis_tickmode="array",
        xaxis_tickvals=hours,            # показывать часы в правильном порядке
        xaxis_ticktext=hours,
        title_x=0.5,
        bargap=0.1
    )

    fig.show()

if __name__ == "__main__":
    run_time_slider()
