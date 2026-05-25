-- ============================================================
--  Personal Finance Analysis — SQL Portfolio Project
--  Author : Jose
--  Tools  : SQLite  (compatible with PostgreSQL with minor tweaks)
--  Tables : transactions, category_budgets
-- ============================================================
--
--  TABLE SCHEMAS
--  ─────────────────────────────────────────────────────────
--  transactions
--    transaction_id  TEXT  PRIMARY KEY
--    date            DATE
--    category        TEXT
--    merchant        TEXT
--    amount          REAL
--    type            TEXT   -- 'Income' | 'Expense'
--    payment_method  TEXT
--    month           TEXT   -- period string  e.g. '2023-01'
--    year            INT
--    month_num       INT
--    month_label     TEXT   -- e.g. 'Jan 2023'
--    is_overspend    INT    -- 0 | 1
--
--  category_budgets
--    category        TEXT  PRIMARY KEY
--    monthly_budget  REAL
-- ============================================================


-- ============================================================
-- Q1 · Total spending by category (all time)
--      Skills: GROUP BY, aggregate functions, ORDER BY
-- ============================================================
SELECT
    category,
    COUNT(*)                          AS num_transactions,
    ROUND(SUM(amount), 2)             AS total_spent,
    ROUND(AVG(amount), 2)             AS avg_per_transaction,
    ROUND(MIN(amount), 2)             AS min_tx,
    ROUND(MAX(amount), 2)             AS max_tx
FROM transactions
WHERE type = 'Expense'
GROUP BY category
ORDER BY total_spent DESC;


-- ============================================================
-- Q2 · Monthly income vs expenses vs net savings
--      Skills: CASE WHEN inside aggregates, derived columns
-- ============================================================
SELECT
    month_label,
    ROUND(SUM(CASE WHEN type = 'Income'  THEN amount ELSE 0 END), 2) AS income,
    ROUND(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 2) AS expenses,
    ROUND(
        SUM(CASE WHEN type = 'Income'  THEN amount ELSE 0 END) -
        SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 2
    )                                                                 AS net_savings,
    ROUND(
        (SUM(CASE WHEN type = 'Income'  THEN amount ELSE 0 END) -
         SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END)) /
         SUM(CASE WHEN type = 'Income'  THEN amount ELSE 0 END) * 100, 1
    )                                                                 AS savings_rate_pct
FROM transactions
GROUP BY month_label, year, month_num
ORDER BY year, month_num;


-- ============================================================
-- Q3 · Budget vs actual spend per category
--      Skills: JOIN, arithmetic on aggregates, CASE WHEN label
-- ============================================================
SELECT
    t.category,
    ROUND(cb.monthly_budget, 2)            AS monthly_budget,
    ROUND(SUM(t.amount) / 24.0, 2)        AS avg_monthly_actual,
    ROUND(SUM(t.amount) / 24.0
          - cb.monthly_budget, 2)          AS avg_monthly_variance,
    CASE
        WHEN SUM(t.amount) / 24.0 > cb.monthly_budget THEN 'Over budget'
        ELSE 'Within budget'
    END                                    AS budget_status
FROM transactions t
JOIN category_budgets cb
  ON t.category = cb.category
WHERE t.type = 'Expense'
GROUP BY t.category, cb.monthly_budget
ORDER BY avg_monthly_variance DESC;


-- ============================================================
-- Q4 · Top 10 merchants by total spend
--      Skills: GROUP BY multiple columns, LIMIT
-- ============================================================
SELECT
    merchant,
    category,
    COUNT(*)                   AS num_visits,
    ROUND(SUM(amount), 2)      AS total_spent,
    ROUND(AVG(amount), 2)      AS avg_per_visit
FROM transactions
WHERE type = 'Expense'
GROUP BY merchant, category
ORDER BY total_spent DESC
LIMIT 10;


-- ============================================================
-- Q5 · Months where any category exceeded budget
--      Skills: JOIN, GROUP BY, HAVING to filter aggregates
-- ============================================================
SELECT
    t.month_label,
    t.category,
    ROUND(cb.monthly_budget, 2)    AS budget,
    ROUND(SUM(t.amount), 2)        AS actual_spent,
    ROUND(SUM(t.amount)
          - cb.monthly_budget, 2)  AS overspend_amount
FROM transactions t
JOIN category_budgets cb
  ON t.category = cb.category
WHERE t.type = 'Expense'
GROUP BY t.month_label, t.year, t.month_num, t.category, cb.monthly_budget
HAVING actual_spent > cb.monthly_budget
ORDER BY overspend_amount DESC;


-- ============================================================
-- Q6 · Payment method breakdown with % share
--      Skills: window function SUM() OVER() for percentage
-- ============================================================
SELECT
    payment_method,
    COUNT(*)                          AS num_transactions,
    ROUND(SUM(amount), 2)             AS total_spent,
    ROUND(AVG(amount), 2)             AS avg_transaction,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER(), 1)    AS pct_of_total_txns
FROM transactions
WHERE type = 'Expense'
GROUP BY payment_method
ORDER BY total_spent DESC;


-- ============================================================
-- Q7 · Year-over-year spending comparison by category
--      Skills: conditional aggregation, YOY % change formula
-- ============================================================
SELECT
    category,
    ROUND(SUM(CASE WHEN year = 2023 THEN amount ELSE 0 END), 2) AS spend_2023,
    ROUND(SUM(CASE WHEN year = 2024 THEN amount ELSE 0 END), 2) AS spend_2024,
    ROUND(
        (SUM(CASE WHEN year = 2024 THEN amount ELSE 0 END) -
         SUM(CASE WHEN year = 2023 THEN amount ELSE 0 END)) /
         SUM(CASE WHEN year = 2023 THEN amount ELSE 0 END) * 100, 1
    )                                                            AS yoy_change_pct
FROM transactions
WHERE type = 'Expense'
GROUP BY category
ORDER BY yoy_change_pct DESC;


-- ============================================================
-- Q8 · Rolling 3-month average spend — discretionary categories
--      Skills: CTE, window function AVG() OVER(ROWS PRECEDING)
-- ============================================================
WITH monthly_disc AS (
    SELECT
        year,
        month_num,
        month_label,
        ROUND(SUM(CASE WHEN category = 'Groceries'     THEN amount ELSE 0 END), 2) AS groceries,
        ROUND(SUM(CASE WHEN category = 'Dining Out'    THEN amount ELSE 0 END), 2) AS dining_out,
        ROUND(SUM(CASE WHEN category = 'Entertainment' THEN amount ELSE 0 END), 2) AS entertainment,
        ROUND(SUM(CASE WHEN category = 'Shopping'      THEN amount ELSE 0 END), 2) AS shopping
    FROM transactions
    WHERE type = 'Expense'
    GROUP BY year, month_num, month_label
)
SELECT
    month_label,
    groceries,
    dining_out,
    entertainment,
    shopping,
    ROUND(AVG(groceries)  OVER (ORDER BY year, month_num ROWS 2 PRECEDING), 2) AS groceries_3mo_avg,
    ROUND(AVG(dining_out) OVER (ORDER BY year, month_num ROWS 2 PRECEDING), 2) AS dining_3mo_avg,
    ROUND(AVG(shopping)   OVER (ORDER BY year, month_num ROWS 2 PRECEDING), 2) AS shopping_3mo_avg
FROM monthly_disc
ORDER BY year, month_num;
