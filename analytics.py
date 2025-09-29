import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from openpyxl.formatting.rule import ColorScaleRule
from config import DB_CONFIG

# ======================
# Загрузка SQL-запросов
# ======================
def load_queries(sql_file="queries.sql"):
    queries = {}
    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()
    raw_queries = [q.strip() for q in content.split(";") if q.strip()]
    for i, query in enumerate(raw_queries, start=1):
        queries[f"query_{i}"] = query
    return queries


# ======================
# Экспорт в Excel с форматированием + лимит строк
# ======================
def export_to_excel(dataframes_dict, filename):
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)

    MAX_ROWS = 1_048_000  # лимит Excel

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        total_rows = 0
        for sheet_name, df in dataframes_dict.items():
            if len(df) > MAX_ROWS:
                print(f"⚠️ {sheet_name}: {len(df)} строк → обрезаем до {MAX_ROWS}")
                df = df.iloc[:MAX_ROWS]  # берём первые строки

            df.to_excel(writer, sheet_name=sheet_name, index=False)
            total_rows += len(df)

            # --- форматирование ---
            ws = writer.sheets[sheet_name]

            # закрепляем шапку
            ws.freeze_panes = "B2"

            # фильтры
            ws.auto_filter.ref = ws.dimensions

            # условное форматирование для числовых колонок
            for col_idx, col in enumerate(df.columns, 1):
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_letter = ws.cell(row=1, column=col_idx).column_letter
                    cell_range = f"{col_letter}2:{col_letter}{len(df)+1}"
                    rule = ColorScaleRule(
                        start_type="min", start_color="FFAA0000",
                        mid_type="percentile", mid_value=50, mid_color="FFFFFF00",
                        end_type="max", end_color="FF00AA00"
                    )
                    ws.conditional_formatting.add(cell_range, rule)

    print(f"✅ Создан файл {filepath}, {len(dataframes_dict)} листов, {total_rows} строк (с учётом обрезки)")


# ======================
# Plotly интерактив
# ======================
def run_time_slider():
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Успешное подключение к базе данных")

    queries = load_queries("queries.sql")
    if "query_11" not in queries:
        raise ValueError("❌ В queries.sql нет query_11 для временного ползунка")

    df = pd.read_sql(queries["query_11"], conn)
    conn.close()
    print(f"📊 Получено строк: {len(df)}")

    dow_map = {
        0: "Воскресенье", 1: "Понедельник", 2: "Вторник",
        3: "Среда", 4: "Четверг", 5: "Пятница", 6: "Суббота"
    }
    df["order_dow"] = df["order_dow"].map(dow_map)
    df["order_hour_str"] = df["order_hour_of_day"].astype(int).apply(lambda x: f"{x:02d}:00")

    dow_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    hours = [f"{h:02d}:00" for h in range(24)]

    df["order_dow"] = pd.Categorical(df["order_dow"], categories=dow_order, ordered=True)
    df["order_hour_str"] = pd.Categorical(df["order_hour_str"], categories=hours, ordered=True)

    counts = df.groupby(["order_dow", "order_hour_str"]).size().reset_index(name="total_orders")

    idx = pd.MultiIndex.from_product([dow_order, hours], names=["order_dow", "order_hour_str"])
    full = counts.set_index(["order_dow", "order_hour_str"]).reindex(idx, fill_value=0).reset_index()

    fig = px.bar(
        full,
        x="order_hour_str", y="total_orders",
        animation_frame="order_dow",
        category_orders={"order_dow": dow_order, "order_hour_str": hours},
        labels={"order_hour_str": "Час заказа", "total_orders": "Количество заказов", "order_dow": "День недели"},
        title="📊 Количество заказов по часам (ползунок — день недели)"
    )

    fig.update_layout(
        xaxis_tickangle=0,
        xaxis_tickmode="array",
        xaxis_tickvals=hours,
        xaxis_ticktext=hours,
        title_x=0.5,
        bargap=0.1
    )

    fig.show()


# ======================
# Matplotlib аналитика
# ======================
charts_dir = os.path.join(os.getcwd(), "charts")
os.makedirs(charts_dir, exist_ok=True)

GRAPH_MAP = {
    "query_1": {"type": "bar", "title": "Топ-10 популярных продуктов", "xlabel": "Продукты", "ylabel": "Количество заказов"},
    "query_2": {"type": "hbar", "title": "Популярность категорий (aisles)", "xlabel": "Количество заказов", "ylabel": "Категории"},
    "query_3": {"type": "pie", "title": "Доли департаментов в заказах"},
    "query_5": {"type": "line", "title": "Количество заказов по часам суток", "xlabel": "Час дня", "ylabel": "Количество заказов"},
    "query_6": {"type": "hist", "title": "Распределение числа товаров в заказах", "xlabel": "Количество товаров", "ylabel": "Частота"},
    "query_10": {"type": "scatter", "title": "Продукты, которые чаще всего заказывают вместе", "xlabel": "Продукт 1 (индекс)", "ylabel": "Частота совместных заказов"}
}

def plot_pie(df, title, threshold=2.5):
    """
    Построение круговой диаграммы с объединением мелких категорий в 'Другие'.
    df: DataFrame с 2 колонками (label, value)
    title: Заголовок графика
    threshold: минимальный процент, ниже которого категории объединяются
    """
    total = df.iloc[:, 1].sum()
    df["pct"] = df.iloc[:, 1] / total * 100

    large = df[df["pct"] >= threshold]
    small = df[df["pct"] < threshold]

    if not small.empty:
        other_row = pd.DataFrame({
            df.columns[0]: ["Другие"],
            df.columns[1]: [small.iloc[:, 1].sum()],
            "pct": [small["pct"].sum()]
        })
        df_plot = pd.concat([large, other_row], ignore_index=True)
    else:
        df_plot = df.copy()

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        df_plot.iloc[:, 1],
        labels=None,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.8,
        textprops={'fontsize': 10}
    )

    ax.legend(
        wedges, df_plot.iloc[:, 0],
        title="Категории",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10
    )

    plt.title(title, fontsize=14)
    return plt

def plot_bar(df, meta):
    df.plot(kind="bar", x=df.columns[0], y=df.columns[1], legend=False)
    plt.xlabel(meta["xlabel"]); plt.ylabel(meta["ylabel"]); plt.title(meta["title"])

def plot_hbar(df, meta):
    df.plot(kind="barh", x=df.columns[0], y=df.columns[1], legend=False)
    plt.xlabel(meta["xlabel"]); plt.ylabel(meta["ylabel"]); plt.title(meta["title"])

def plot_line(df, meta):
    df.plot(kind="line", x=df.columns[0], y=df.columns[1], marker="o")
    plt.xlabel(meta["xlabel"]); plt.ylabel(meta["ylabel"]); plt.title(meta["title"])

def plot_hist(df, meta, bins=20, cap_percentile=0.99):
    """
    Рисует гистограмму по колонке 'product_count' (или по первому подходящему числовому столбцу).
    По умолчанию обрезает верхние 1% значений для читаемости (cap_percentile).
    """
    # выбрать колонку
    if "product_count" in df.columns:
        col = "product_count"
    else:
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        # попробуем исключить order_id/user_id, если они есть
        candidates = [c for c in num_cols if c not in ("order_id", "user_id")]
        col = candidates[0] if candidates else (num_cols[0] if num_cols else None)

    if col is None:
        print("⚠️ Нет числовых колонок для гистограммы.")
        return

    # обрезаем экстремумы для наглядности
    cap = df[col].quantile(cap_percentile)
    data = df[df[col] <= cap][col]

    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins)
    plt.xlabel(meta.get("xlabel", col))
    plt.ylabel(meta.get("ylabel", "Частота"))
    plt.title(meta.get("title", f"Гистограмма по {col}"))
    plt.axvline(data.median(), color="k", linestyle="--", label=f"median={data.median():.0f}")
    plt.legend()
    return plt


def plot_scatter(df, meta):
    # берем топ-20 записей
    df = df.head(20).reset_index(drop=True)

    # продукт 1 и продукт 2 можно склеить в подпись
    df["pair"] = df[df.columns[0]] + " + " + df[df.columns[1]]

    plt.figure(figsize=(12, 6))
    plt.scatter(df["pair"], df[df.columns[2]], s=100, alpha=0.7, c="blue")

    plt.xticks(rotation=90, fontsize=9)
    plt.ylabel(meta["ylabel"])
    plt.title(meta["title"])
    plt.tight_layout()
    return plt


def run_analytics():
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Успешное подключение к базе данных")

    queries = load_queries("queries.sql")
    report_dfs = {}

    for qname, meta in GRAPH_MAP.items():
        if qname not in queries:
            print(f"⚠️ Запрос {qname} не найден в queries.sql")
            continue

        print(f"\n🔹 Выполняется {qname}: {meta['title']}")
        df = pd.read_sql(queries[qname], conn)
        report_dfs[qname] = df
        print(f"Получено строк: {len(df)}")

        plt.figure(figsize=(10, 6))
        if meta["type"] == "bar": plot_bar(df, meta)
        elif meta["type"] == "hbar": plot_hbar(df, meta)
        elif meta["type"] == "pie": plt.close(); plot_pie(df, meta["title"])
        elif meta["type"] == "line": plot_line(df, meta)
        elif meta["type"] == "hist": plot_hist(df, meta)
        elif meta["type"] == "scatter": plot_scatter(df, meta)

        file_path = os.path.join(charts_dir, f"{qname}.png")
        plt.tight_layout(); plt.savefig(file_path); plt.close()
        print(f"📊 Сохранён график: {file_path}")

    conn.close()

    # Экспорт в Excel (третье задание)
    export_to_excel(report_dfs, "instacart_report.xlsx")

    print("\n✅ Все графики сохранены и Excel отчёт создан в /exports/")


# ======================
# Запуск
# ======================
if __name__ == "__main__":
    run_time_slider()
    run_analytics()
