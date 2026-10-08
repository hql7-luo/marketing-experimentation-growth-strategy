-- Intention to treat: every randomized customer remains in the denominator.
SELECT action, COUNT(*) AS assigned_customers,
       SUM(visit) AS visitors, AVG(visit) AS visit_rate,
       SUM(conversion) AS buyers, AVG(conversion) AS conversion_rate,
       AVG(spend) AS spend_per_assigned_customer,
       AVG(history) AS historical_spend, AVG(recency) AS recency_months
FROM customers GROUP BY action ORDER BY action;
