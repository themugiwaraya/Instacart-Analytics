-- 1. Проверка: первые 10 строк из таблицы products
SELECT * FROM products LIMIT 10;

-- 2. Фильтрация и сортировка: продукты из отдела "snacks", отсортированные по имени
SELECT product_id, product_name
FROM products
WHERE department_id = 19
ORDER BY product_name ASC
LIMIT 20;

-- 3. Количество заказов по дням недели
SELECT order_dow, COUNT(*) AS total_orders
FROM orders
GROUP BY order_dow
ORDER BY order_dow;

-- 4. Среднее количество товаров в заказе
SELECT AVG(product_count) 
FROM (
    SELECT order_id, COUNT(*) AS product_count
    FROM order_products_prior
    GROUP BY order_id
) t;

-- 5. Минимальное и максимальное количество товаров в заказе
SELECT MIN(product_count), MAX(product_count)
FROM (
    SELECT order_id, COUNT(*) AS product_count
    FROM order_products_prior
    GROUP BY order_id
) t;

-- 6. JOIN: топ-10 популярных продуктов
SELECT p.product_name, COUNT(*) AS times_ordered
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY p.product_name
ORDER BY times_ordered DESC
LIMIT 10;

-- ========================
-- 10 аналитических запросов
-- ========================

-- 1. Топ-10 популярных продуктов
SELECT p.product_name, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_orders DESC
LIMIT 10;

-- 2. Популярность категорий (aisles)
SELECT a.aisle, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
JOIN aisles a ON p.aisle_id = a.aisle_id
GROUP BY a.aisle
ORDER BY total_orders DESC
LIMIT 10;

-- 3. Популярность департаментов
SELECT d.department, COUNT(*) AS total_orders
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
JOIN departments d ON p.department_id = d.department_id
GROUP BY d.department
ORDER BY total_orders DESC;

-- 4. Активность заказов по дням недели
SELECT order_dow, COUNT(*) AS total_orders
FROM orders
GROUP BY order_dow
ORDER BY order_dow;

-- 5. Активность заказов по часам суток
SELECT order_hour_of_day, COUNT(*) AS total_orders
FROM orders
GROUP BY order_hour_of_day
ORDER BY order_hour_of_day;

-- 6. Среднее количество товаров в заказе
SELECT AVG(product_count) 
FROM (
    SELECT order_id, COUNT(*) AS product_count
    FROM order_products_prior
    GROUP BY order_id
) t;

-- 7. Повторные заказы (reordered)
SELECT reordered, COUNT(*) 
FROM order_products_prior
GROUP BY reordered;

-- 8. Самые "лояльные" продукты (с наибольшим % повторных заказов)
SELECT p.product_name,
       COUNT(*) FILTER (WHERE reordered = 1) * 100.0 / COUNT(*) AS reorder_rate
FROM order_products_prior opp
JOIN products p ON opp.product_id = p.product_id
GROUP BY p.product_name
HAVING COUNT(*) > 50
ORDER BY reorder_rate DESC
LIMIT 10;

-- 9. Среднее время между заказами (days_since_prior_order)
SELECT AVG(days_since_prior_order) 
FROM orders
WHERE days_since_prior_order IS NOT NULL;

-- 10. Продукты, которые чаще всего заказывают вместе
SELECT p1.product_name AS product_1,
       p2.product_name AS product_2,
       COUNT(*) AS together_count
FROM order_products_prior opp1
JOIN order_products_prior opp2 ON opp1.order_id = opp2.order_id 
    AND opp1.product_id < opp2.product_id
JOIN products p1 ON opp1.product_id = p1.product_id
JOIN products p2 ON opp2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY together_count DESC
LIMIT 10;
