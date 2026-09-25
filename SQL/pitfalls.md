Find the percentage of shipable orders.

Consider an order is shipable if the customer's address is known.

<img width="480" alt="orders and customers schema" src="https://github.com/user-attachments/assets/39b1e5ff-5aa2-4767-b29c-a655ff2843ae">

Pitfall:- Because COUNT() returns an integer, count(address) / count(*) will evaluate to 0 whenever count(address) < count(*), resulting in 0 or 0.0 as your percentage.

Edge Case:- Division by Zero: If the join yields zero rows, count(*) is 0, leading to a division-by-zero error.

Solution Approach

```sql
SELECT 
    COUNT(*) AS total_orders,
    COUNT(c.address) AS orders_with_address,
    (COUNT(c.address) * 100.0 / NULLIF(COUNT(*), 0)) AS percentage
FROM orders o 
JOIN customers c
  ON o.cust_id = c.id;
```

In SQL arithmetic, dividing by NULL does not throw an error—any arithmetic operation involving NULL yields NULL (following standard three-valued logic).

The definition of NULLIF(a, b) in SQL is: "If $a$ equals $b$, return NULL. Otherwise, return $a$." Internally, SQL evaluates NULLIF(a, b) as this shorthand CASE expression:

```sql
CASE 
    WHEN a = b THEN NULL 
    ELSE a 
END
```
