SELECT customer_segment, action, COUNT(*) AS assigned_customers,
       AVG(conversion) AS conversion_rate, AVG(spend) AS spend_per_assigned_customer
FROM customers GROUP BY customer_segment, action ORDER BY customer_segment, action;
