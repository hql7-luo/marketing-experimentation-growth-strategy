-- All dimensions were measured before assignment. "mens" is purchase history, not gender.
SELECT channel, zip_code, COUNT(*) AS customers,
       AVG(history) AS historical_spend, AVG(recency) AS recency_months,
       AVG(newbie) AS share_new_customers
FROM customers GROUP BY channel, zip_code ORDER BY customers DESC;
