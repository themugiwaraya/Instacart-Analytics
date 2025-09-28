-- 1. Топ-10 популярных продуктов (по заказам) Bar chart
SELECT p.product_name, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_orders DESC
LIMIT 10;

-- 2. Популярность категорий (aisles) Horizontal bar chart
SELECT a.aisle, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
JOIN aisles a ON p.aisle_id = a.aisle_id
GROUP BY a.aisle
ORDER BY total_orders DESC
LIMIT 10;

-- 3. Доли департаментов (departments) в заказах Pie chart
SELECT d.department, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
JOIN departments d ON p.department_id = d.department_id
GROUP BY d.department
ORDER BY total_orders DESC;

-- 4. Среднее количество товаров в заказе по дням недели Line chart
SELECT o.order_dow, AVG(t.product_count) AS avg_products
FROM (
    SELECT order_id, COUNT(*) AS product_count
    FROM order_products_prior
    GROUP BY order_id
) t
JOIN orders o ON t.order_id = o.order_id
GROUP BY o.order_dow
ORDER BY o.order_dow;


-- 5. Количество заказов по часам суток Line chart
SELECT o.order_hour_of_day, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN orders o ON opp.order_id = o.order_id
GROUP BY o.order_hour_of_day
ORDER BY o.order_hour_of_day;


-- 6. Распределение числа товаров в заказах Pie chart
SELECT t.product_count
FROM (
    SELECT order_id, COUNT(*) AS product_count
    FROM order_products_prior
    GROUP BY order_id
) t;


-- 7. Повторные vs новые заказы Pie chart
SELECT CASE WHEN opp.reordered = 1 THEN 'Повторный' ELSE 'Новый' END AS order_type,
       COUNT(*) AS total
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY order_type;


-- 8. Самые лояльные продукты (с высоким % повторных заказов) Bar chart
SELECT p.product_name,
       ROUND(COUNT(*) FILTER (WHERE opp.reordered = 1) * 100.0 / COUNT(*), 2) AS reorder_rate
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY p.product_name
HAVING COUNT(*) > 50
ORDER BY reorder_rate DESC
LIMIT 10;


-- 9. Среднее время между заказами по дням недели Line chart
SELECT o.order_dow, AVG(o.days_since_prior_order) AS avg_days
FROM orders o
JOIN order_products_prior opp ON o.order_id = opp.order_id
WHERE o.days_since_prior_order IS NOT NULL
GROUP BY o.order_dow
ORDER BY o.order_dow;

-- 10. Продукты, которые чаще всего заказывают вместе Scatter plot or Heatmap
WITH top_products AS (
    SELECT p.product_id, p.product_name
    FROM order_products_prior opp
    JOIN products p ON opp.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY COUNT(*) DESC
    LIMIT 50
)
SELECT p1.product_name AS product_1,
       p2.product_name AS product_2,
       COUNT(*) AS together_count
FROM order_products_prior opp1
JOIN order_products_prior opp2 
     ON opp1.order_id = opp2.order_id AND opp1.product_id < opp2.product_id
JOIN top_products p1 ON opp1.product_id = p1.product_id
JOIN top_products p2 ON opp2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY together_count DESC
LIMIT 10;

-- 11. Заказы с датами для временного анализа (для Plotly slider)
SELECT 
    o.order_id,
    o.user_id,
    o.order_number,
    o.order_dow,
    o.order_hour_of_day,
    o.days_since_prior_order
FROM orders o
ORDER BY o.order_id
LIMIT 5000;  -- ограничиваем, чтобы график был быстрее
