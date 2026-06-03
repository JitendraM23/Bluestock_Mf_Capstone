# Bluestock Capstone Project - Data Dictionary

This data dictionary serves as the central reference manual for the `bluestock_mf.db` star schema database. It provides explicit schemas, metric definitions, and column constraints for all relational tables generated during the Day 2 ETL pipeline.


## 1. Dimension Tables (Categorical Lookup Layouts)

### `dim_fund`
 **Description:** Master directory containing unique tracking metadata for all available Mutual Fund schemes.
 **Primary Key:** `amfi_code`
 **Source Reference:** `cleaned_fund_master.csv`

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Unique 6-digit code issued by the Association of Mutual Funds in India. |
| `fund_house` | TEXT | NOT NULL | The Asset Management Company (AMC) managing the fund (e.g., SBI Mutual Fund). |
| `scheme_name` | TEXT | NOT NULL | The specific name of the mutual fund investment plan. |
| `category` | TEXT | NOT NULL | Asset class division (e.g., Equity, Debt, Hybrid). |
| `sub_category` | TEXT | NOT NULL | Specific investment strategy classification (e.g., Small Cap, Large Cap). |
| `plan` | TEXT | NOT NULL | Distribution plan identifier (Direct Plan vs. Regular Plan). |
| `launch_date` | TEXT | None | The official start date when the fund went live. |
| `benchmark` | TEXT | None | The index against which the fund's performance is measured (e.g., NIFTY 50). |
| `fund_manager` | TEXT | None | The professional portfolio manager executing the fund strategy. |
| `risk_category`| TEXT | None | Qualitative baseline risk assessment level (e.g., Moderate, Very High). |
| `sebi_category_code`| TEXT| None | Standard regulatory category code assigned by SEBI. |

### `dim_date`
 **Description:** Chronological timeline tracking directory used to optimize time-series queries.
 **Primary Key:** `date_id`
 **Source Reference:** Dynamically generated pipeline dimension (2022–2026).

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `date_id` | TEXT | PRIMARY KEY | Calendar tracking date stored as string format (`YYYY-MM-DD`). |
| `year` | INTEGER | NOT NULL | Four-digit calendar year. |
| `month` | INTEGER | NOT NULL | Calendar month index number (1 to 12). |
| `day` | INTEGER | NOT NULL | Day of the month index number (1 to 31). |
| `quarter` | INTEGER | NOT NULL | Fiscal quarter tracking index number (1 to 4). |
| `is_weekend` | INTEGER | NOT NULL | Flag indicating weekend alignment: `1` = Saturday/Sunday, `0` = Weekday. |

---

## 2. Fact Tables (Quantitative Financial Metrics)

### `fact_nav`
 **Description:** Time-series tracker maintaining historical records of daily fund share valuations.
 **Primary Key:** `nav_id` (Autoincremented)
 **Source Reference:** `cleaned_nav_history.csv`

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `nav_id` | INTEGER | PRIMARY KEY | Internal system-generated surrogate key tracking row records. |
| `amfi_code` | INTEGER | FOREIGN KEY | Links directly back to `dim_fund(amfi_code)`. |
| `date` | TEXT | FOREIGN KEY | Valuation day, linking directly to `dim_date(date_id)`. |
| `nav` | REAL | NOT NULL | Net Asset Value (Per-share price of the fund for that day). |

### `fact_transactions`
 **Description:** Operational logging matrix capturing retail investor transactional entries.
 **Primary Key:** `transaction_id`
 **Source Reference:** `cleaned_investor_transactions.csv`

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `transaction_id` | TEXT | PRIMARY KEY | Unique alpha-numeric tracking sequence code for the investment entry. |
| `transaction_date`| TEXT | FOREIGN KEY | Date execution occurred, linking to `dim_date(date_id)`. |
| `amfi_code` | INTEGER | FOREIGN KEY | Targeted fund code, linking to `dim_fund(amfi_code)`. |
| `transaction_type`| TEXT | NOT NULL | Style of trade execute movement (`SIP` / `Lumpsum` / `Redemption`). |
| `amount_inr` | INTEGER | NOT NULL | Absolute transactional value represented in Indian Rupees (₹). |
| `state` | TEXT | None | Geographic state location of the retail investor. |
| `city` | TEXT | None | Geographic city location of the retail investor. |
| `city_tier` | TEXT | None | Market category classification division tier (`T30` or `B30`). |
| `age_group` | TEXT | None | Target generation demographic band of the investor. |
| `gender` | TEXT | None | Biological gender classification of the investor. |
| `annual_income_lakh`| REAL| None | Self-reported yearly income bracket represented in Lakhs. |
| `payment_mode` | TEXT | None | Gateway mechanism utilized for funding (`UPI`, `Net Banking`, `Cheque`). |
| `kyc_status` | TEXT | None | Regulatory documentation compliance flag (`Verified` or `Pending`). |

### `fact_performance`
 **Description:** Analytical ledger monitoring risk coefficients, return margins, and operational costs.
 **Primary Key:** `amfi_code`
 **Source Reference:** `cleaned_scheme_performance.csv`

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Matches 1-to-1 with `dim_fund(amfi_code)` serving as structural extension. |
| `return_1yr_pct` | REAL | None | Total return gains accumulated across trailing 12-month window. |
| `return_3yr_pct` | REAL | None | Annualized return performance across trailing 36-month window. |
| `return_5yr_pct` | REAL | None | Annualized return performance across trailing 60-month window. |
| `benchmark_3yr_pct`| REAL | None | Annualized returns yielded by fund's tracking index over 3 years. |
| `alpha` | REAL | None | Outperformance metric against benchmark risk (Positive = excess value). |
| `beta` | REAL | None | Volatility factor relative to broader market (Base standard = 1.0). |
| `sharpe_ratio` | REAL | None | Risk-adjusted return performance efficiency score. |
| `sortino_ratio` | REAL | None | Downside risk-adjusted performance efficiency profile score. |
| `std_dev_ann_pct`| REAL | None | Historical pricing spread variance volatility width measurement. |
| `max_drawdown_pct`| REAL | None | Peak-to-trough drop depth percentage over historical timeline. |
| `expense_ratio_pct`| REAL | None | Aggregate internal operating fee rate charged by AMC to investors. |
| `morningstar_rating`| INTEGER| None | Quantitative performance star evaluation ranking tier (1 to 5 Stars). |
| `risk_grade` | TEXT | None | Consolidated risk tier valuation assignment (e.g., Low, High). |
| `expense_anomaly` | INTEGER | NOT NULL | Custom pipeline data quality flag: `1` = Out of bounds, `0` = Nominal range. |

### `fact_aum`
 **Description:** Macro-level financial registry tracking macro assets held by underlying AMC managers.
 **Primary Key:** `aum_id` (Autoincremented)
 **Source Reference:** `cleaned_aum_by_fund_house.csv`

| Column Name | Data Type | Constraints | Business Definition / Context |
| :--- | :--- | :--- | :--- |
| `aum_id` | INTEGER | PRIMARY KEY | System surrogate tracking index generated per row entry. |
| `date` | TEXT | FOREIGN KEY | Logging timeline tracking point, linking to `dim_date(date_id)`. |
| `fund_house` | TEXT | NOT NULL | Targeted Asset Management Company lookup text string. |
| `aum_lakh_crore` | REAL | None | Absolute Assets Under Management tracked in Lakh Crores. |
| `aum_crore` | INTEGER | None | Absolute Assets Under Management translated cleanly to Crores. |
| `num_schemes` | INTEGER | None | Aggregate volume of operational funds active under the AMC umbrella. |