-- Alec Sirkin
-- CSCI-SHU 213 Databases
-- Course project part 3: example queries

SELECT * FROM flight WHERE `status` = 'upcoming';

SELECT * FROM flight WHERE `status` = 'delayed';

SELECT customer.name 
FROM customer INNER JOIN purchases ON (purchases.customer_email = customer.email) 
WHERE (purchases.booking_agent_id IS NOT NULL);

SELECT * FROM airplane WHERE airline_name = 'Cathay Pacific';

