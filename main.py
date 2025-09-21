import psycopg2
import pandas as pd
import os

DB_NAME = "instacart_db"
DB_USER = "postgres"      
DB_PASS = "0000"          
DB_HOST = "localhost"
DB_PORT = "5432"

QUERIES = {
    "top_products": """
        SELECT p.product_name, COUNT(*) AS total_orders
        FROM order_products_prior opp
        JOIN products p ON opp.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY total_orders DESC
        LIMIT 10;
    """,
    "orders_by_dow": """
        SELECT order_dow, COUNT(*) AS total_orders
        FROM orders
        GROUP BY order_dow
        ORDER BY order_dow;
    """,
    "reorder_rate": """
        SELECT reordered, COUNT(*) AS cnt
        FROM order_products_prior
        GROUP BY reordered;
    """
}

def run_queries():
    try:
        os.makedirs("output", exist_ok=True)

        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        print("✅ Успешное подключение к базе данных")

        for name, query in QUERIES.items():
            print(f"\n🔹 Результат: {name}")
            df = pd.read_sql(query, conn)
            print(df.head())
            df.to_csv(f"output/{name}.csv", index=False, encoding="utf-8")
            print(f"💾 Сохранено в output/{name}.csv")

        conn.close()

    except Exception as e:
        print("❌ Ошибка подключения или выполнения запроса:", e)

if __name__ == "__main__":
    run_queries()