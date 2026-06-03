
-- Explains which Asset Management Companies (AMCs) control the most capital.
SELECT 
    fund_house, 
    MAX(aum_crore) AS peak_aum_crore,
    num_schemes
FROM fact_aum
GROUP BY fund_house
ORDER BY peak_aum_crore DESC
LIMIT 5;

-- Connects the NAV history fact table with the Date dimension to track monthly pricing trends chronologically.
SELECT 
    d.year, 
    d.month, 
    f.scheme_name, 
    ROUND(AVG(n.nav), 2) AS average_monthly_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date_id
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY d.year, d.month, n.amfi_code
ORDER BY d.year ASC, d.month ASC, average_monthly_nav DESC;

-- Uses a subquery to sum up total SIP transaction amounts by year and calculates the percentage growth rate.
WITH yearly_sip AS (
    SELECT 
        d.year, 
        SUM(t.amount_inr) AS total_sip_amount
    FROM fact_transactions t
    JOIN dim_date d ON t.transaction_date = d.date_id
    WHERE t.transaction_type = 'Sip'
    GROUP BY d.year
)
SELECT 
    curr.year AS current_year,
    curr.total_sip_amount AS current_year_volume,
    prev.year AS previous_year,
    prev.total_sip_amount AS previous_year_volume,
    ROUND(((curr.total_sip_amount - prev.total_sip_amount) * 100.0 / prev.total_sip_amount), 2) AS yoy_growth_percentage
FROM yearly_sip curr
LEFT JOIN yearly_sip prev ON curr.year = prev.year + 1;

-- Aggregates geographical data to identify which regions generate the highest investment volumes.
SELECT 
    state, 
    COUNT(transaction_id) AS total_transaction_count,
    SUM(amount_inr) AS total_invested_volume_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_invested_volume_inr DESC;

-- Filters out expensive actively managed funds to pinpoint consumer-friendly low-cost investment options.
SELECT 
    f.amfi_code, 
    f.scheme_name, 
    f.category, 
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;

-- Ranks funds by long-term investment efficacy.
SELECT 
    f.scheme_name, 
    f.category, 
    p.return_5yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_5yr_pct IS NOT NULL
ORDER BY p.return_5yr_pct DESC
LIMIT 5;

-- Measures capital density across Tier 1, Tier 2, and Tier 3 cities.
SELECT 
    city_tier, 
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS cumulative_volume_inr
FROM fact_transactions
GROUP BY city_tier
ORDER BY cumulative_volume_inr DESC;

-- Pinpoints underperforming funds that take massive risks without generating market-beating returns.
SELECT 
    f.scheme_name, 
    p.risk_grade, 
    p.alpha, 
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.risk_grade = 'High' AND p.alpha < 0
ORDER BY p.alpha ASC;

-- Evaluates demographic participation rates and absolute capital allocation volumes.
SELECT 
    gender, 
    COUNT(*) AS investment_count,
    SUM(amount_inr) AS total_capital_allocated_inr,
    ROUND(AVG(amount_inr), 2) AS average_ticket_size_inr
FROM fact_transactions
GROUP BY gender;

-- Summarizes our custom pipeline data-quality flags to see which categories contain out-of-bounds expenses.
SELECT 
    f.category, 
    SUM(p.expense_anomaly) AS total_flagged_anomalies
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY total_flagged_anomalies DESC;