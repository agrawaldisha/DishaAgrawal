# 🗄️ SQL Patterns — Zero to Advanced

> A complete reference of every pattern you'll encounter in SQL problems.  
> Learn these patterns and you can solve **any** SQL problem.

---

## 🟢 Level 0 — Absolute Basics

---

### Pattern 1 — Simple SELECT & Filter

**When to use:** Fetch rows that match a condition.

```sql
SELECT column1, column2
FROM table_name
WHERE condition;
```

**Example:** Get all employees with salary > 50000

```sql
SELECT name, salary
FROM employees
WHERE salary > 50000;
```

---

### Pattern 2 — Sort Results

**When to use:** Order your output by a column.

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC;   -- DESC = highest first, ASC = lowest first
```

---

### Pattern 3 — Limit Results

**When to use:** Get only the top N rows.

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 5;
```

---

## 🟡 Level 1 — Grouping & Aggregation

---

### Pattern 4 — GROUP BY + Aggregate

**When to use:** "Find the total/count/average *per group*"

```sql
SELECT department, COUNT(*) AS total_employees, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

**Common aggregate functions:**

| Function | What it does |
|----------|--------------|
| `COUNT(*)` | Count rows |
| `SUM(col)` | Total of a column |
| `AVG(col)` | Average value |
| `MAX(col)` | Highest value |
| `MIN(col)` | Lowest value |

---

### Pattern 5 — HAVING (Filter on Groups)

**When to use:** Filter *after* grouping. `WHERE` filters rows; `HAVING` filters groups.

> 💡 Rule: If your condition uses an aggregate function → use `HAVING`, not `WHERE`

```sql
SELECT department, COUNT(*) AS total
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;   -- only departments with more than 5 employees
```

**Mental model:**
```
WHERE  → filters ROWS   (before grouping)
HAVING → filters GROUPS (after grouping)
```

---

## 🟠 Level 2 — JOINs

---

### Pattern 6 — INNER JOIN (Most Common)

**When to use:** Combine two tables, keep only matching rows from both.

```sql
SELECT e.name, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;
```

---

### Pattern 7 — LEFT JOIN

**When to use:** Keep ALL rows from the left table, even if no match exists in the right.

```sql
SELECT e.name, o.order_id
FROM employees e
LEFT JOIN orders o ON e.id = o.employee_id;
-- employees with NO orders will still appear (order_id will be NULL)
```

---

### Pattern 8 — Find Rows With No Match (LEFT JOIN + NULL Check)

**When to use:** "Find X that has NO related Y" — a very common interview pattern.

```sql
SELECT e.name
FROM employees e
LEFT JOIN orders o ON e.id = o.employee_id
WHERE o.employee_id IS NULL;
-- This gives employees who have placed ZERO orders
```

> 💡 This is equivalent to `NOT IN` but often faster on large datasets.

---

## 🔵 Level 3 — Subqueries

---

### Pattern 9 — NOT IN Subquery

**When to use:** "Find people who NEVER did X"

```sql
SELECT name
FROM employees
WHERE id NOT IN (
    SELECT employee_id
    FROM orders
    WHERE status = 'cancelled'
);
```

---

### Pattern 10 — Subquery in WHERE (comparison)

**When to use:** Compare a value against an aggregate from another query.

```sql
-- Find employees earning more than the company average
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

---

### Pattern 11 — Subquery in FROM (Derived Table)

**When to use:** You need to query the *result* of another query.

```sql
SELECT department, avg_sal
FROM (
    SELECT department, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department
) AS dept_averages
WHERE avg_sal > 60000;
```

---

### Pattern 12 — EXISTS / NOT EXISTS

**When to use:** Check whether a related row exists (more efficient than `IN` for large tables).

```sql
-- Find customers who have placed at least one order
SELECT name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Find customers who have placed NO orders
SELECT name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

---

## 🟣 Level 4 — CTEs & Readability

---

### Pattern 13 — CTE (WITH clause)

**When to use:** Break a complex query into readable, named steps. Think of it as giving a subquery a name.

```sql
WITH high_earners AS (
    SELECT id, name, salary
    FROM employees
    WHERE salary > 80000
),
their_orders AS (
    SELECT e.name, COUNT(o.id) AS order_count
    FROM high_earners e
    JOIN orders o ON e.id = o.employee_id
    GROUP BY e.name
)
SELECT * FROM their_orders
ORDER BY order_count DESC;
```

> 💡 Always prefer CTEs over nested subqueries — they are much easier to read and debug.

---

### Pattern 14 — Multiple CTEs

**When to use:** Chain multiple steps together like a pipeline.

```sql
WITH step1 AS (...),
     step2 AS (SELECT ... FROM step1 WHERE ...),
     step3 AS (SELECT ... FROM step2 JOIN ...)
SELECT * FROM step3;
```

---

## 🔴 Level 5 — Window Functions (Advanced)

> Window functions perform calculations **across rows related to the current row** without collapsing them into groups.

---

### Pattern 15 — ROW_NUMBER()

**When to use:** Assign a unique rank to each row within a partition.  
Classic use: *"Find the top 1 record per group"*

```sql
SELECT *
FROM (
    SELECT
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn = 1;
-- Gets the highest-paid employee in each department
```

---

### Pattern 16 — RANK() vs DENSE_RANK()

**When to use:** Ranking with ties.

```sql
SELECT name, salary,
    RANK()       OVER (ORDER BY salary DESC) AS rank,        -- 1,2,2,4 (skips 3)
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank   -- 1,2,2,3 (no skip)
FROM employees;
```

| Score | RANK | DENSE_RANK |
|-------|------|------------|
| 100   | 1    | 1          |
| 90    | 2    | 2          |
| 90    | 2    | 2          |
| 80    | 4    | 3          |

---

### Pattern 17 — LAG() / LEAD()

**When to use:** Compare a row with the **previous** or **next** row. Very common in time-series problems.

```sql
SELECT
    order_date,
    revenue,
    LAG(revenue)  OVER (ORDER BY order_date) AS prev_revenue,
    LEAD(revenue) OVER (ORDER BY order_date) AS next_revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_date) AS change
FROM daily_sales;
```

---

### Pattern 18 — Running Total with SUM() OVER

**When to use:** Cumulative sum, running count.

```sql
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (ORDER BY order_date) AS running_total
FROM daily_sales;
```

---

### Pattern 19 — Partitioned Window

**When to use:** Running totals or rankings *within each group* independently.

```sql
SELECT
    department,
    name,
    salary,
    SUM(salary) OVER (PARTITION BY department ORDER BY salary) AS dept_running_total
FROM employees;
```

---

## ⚫ Level 6 — Advanced Patterns

---

### Pattern 20 — Self JOIN

**When to use:** Compare rows in the **same table** to each other.  
Classic use: *Find employees who earn more than their manager.*

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

---

### Pattern 21 — CASE WHEN (Conditional Logic)

**When to use:** Add if/else logic inside a query — pivoting, bucketing, labelling.

```sql
SELECT name, salary,
    CASE
        WHEN salary >= 100000 THEN 'High'
        WHEN salary >= 60000  THEN 'Mid'
        ELSE 'Low'
    END AS salary_band
FROM employees;
```

**Pivot example** — turn rows into columns:

```sql
SELECT
    department,
    SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) AS male_count,
    SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) AS female_count
FROM employees
GROUP BY department;
```

---

### Pattern 22 — COALESCE (Handle NULLs)

**When to use:** Replace NULL with a fallback value.

```sql
SELECT name, COALESCE(phone, email, 'No contact') AS contact
FROM users;
-- Uses phone if not null, else email, else 'No contact'
```

---

### Pattern 23 — Find Nth Highest Value

**When to use:** "Find the 2nd highest salary", "3rd most ordered product", etc.

```sql
-- Using DENSE_RANK (recommended)
SELECT salary
FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employees
) ranked
WHERE rnk = 2;
```

---

### Pattern 24 — Consecutive Rows / Gaps (Island & Gaps)

**When to use:** Detect consecutive streaks, missing dates, gaps in sequences.

```sql
-- Find consecutive login days per user
SELECT user_id,
       login_date,
       login_date - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS grp
FROM logins;
-- Rows in the same streak will have the same `grp` value
```

---

### Pattern 25 — Recursive CTE

**When to use:** Hierarchical data — org charts, folder trees, category trees.

```sql
WITH RECURSIVE org_chart AS (
    -- Base case: top-level manager
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: find their reports
    SELECT e.id, e.name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart ORDER BY level;
```

---

## 🗺️ Quick Pattern Lookup

| Problem says... | Use this pattern |
|-----------------|-----------------|
| "Find people who NEVER did X" | NOT IN / NOT EXISTS / LEFT JOIN + NULL |
| "Count/sum per group" | GROUP BY + Aggregate |
| "Filter a group by count" | HAVING |
| "Top 1 per group" | ROW_NUMBER() OVER (PARTITION BY...) |
| "Nth highest" | DENSE_RANK() |
| "Compare with previous row" | LAG() / LEAD() |
| "Running total" | SUM() OVER (ORDER BY...) |
| "Compare rows in same table" | Self JOIN |
| "If/else in a column" | CASE WHEN |
| "Hierarchy / tree structure" | Recursive CTE |
| "Consecutive streak" | ROW_NUMBER() trick (island & gaps) |
| "Complex multi-step query" | CTEs (WITH clause) |

---

> 📌 **The Golden Rule:** Before writing any SQL, ask yourself — *which pattern does this problem match?*  
> Once you identify the pattern, the query almost writes itself.
