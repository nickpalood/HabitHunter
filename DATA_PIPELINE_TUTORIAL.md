# 🎓 Data Pipeline Tutorial: Simple Budget Tracker
## Prepared for Data Engineering Internship Interview

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Data Pipeline Architecture](#data-pipeline-architecture)
3. [ETL Process Deep Dive](#etl-process-deep-dive)
4. [Data Modeling & Schema Design](#data-modeling--schema-design)
5. [Data Quality & Governance](#data-quality--governance)
6. [How This Relates to DBT & Data Warehousing](#how-this-relates-to-dbt--data-warehousing)
7. [Key Learnings for Your Interview](#key-learnings-for-your-interview)

---

## 🎯 Overview

Your Simple Budget Tracker demonstrates a **complete data pipeline** that handles financial transaction data from ingestion to visualization. This is directly relevant to the internship's focus on **data warehousing, ETL processes, and analytics engineering**.

### Pipeline Summary
```
Raw Data (CSV/Forms) → Extract → Transform → Load → Storage (SQLite) → Analytics → Visualization
```

---

## 🏗️ Data Pipeline Architecture

### Components of Your Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────┤
│  • Revolut CSV Exports (revolut_importer.py)                    │
│  • Manual Form Input (Web UI)                                   │
│  • External APIs (Currency Exchange Rates)                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER (E)                          │
├─────────────────────────────────────────────────────────────────┤
│  • RevolutImporter.parse_csv() - CSV parsing                    │
│  • Flask form handlers - User input capture                     │
│  • API calls to exchangerate-api.com                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  TRANSFORMATION LAYER (T)                        │
├─────────────────────────────────────────────────────────────────┤
│  • Currency Conversion (currency_converter.py)                  │
│  • Merchant Categorization (merchant_mapper.py)                 │
│  • Date Parsing & Standardization                               │
│  • Amount Normalization (to EUR)                                │
│  • Data Validation & Type Checking                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      LOADING LAYER (L)                           │
├─────────────────────────────────────────────────────────────────┤
│  • DataManager.save() - Orchestrates writes                     │
│  • database.py - Connection management                          │
│  • Transaction handling & ACID compliance                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE (SQLite)                       │
├─────────────────────────────────────────────────────────────────┤
│  • users (dimension table)                                      │
│  • expenses (fact table)                                        │
│  • incomes (fact table)                                         │
│  • budgets (dimension table)                                    │
│  • merchant_category_*.json (lookup tables)                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYTICS LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  • Aggregations (totals, averages, trends)                      │
│  • Time-series analysis (monthly trends)                        │
│  • Statistical calculations (linear regression)                 │
│  • Budget vs Actual comparisons                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  • Dashboard (summary KPIs)                                     │
│  • Reports (detailed breakdowns)                                │
│  • Graphs & Charts (trend visualization)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 ETL Process Deep Dive

### 1. **EXTRACT (E)** - Data Ingestion

#### Example: Revolut CSV Import (`api/revolut_importer.py`)

```python
@staticmethod
def parse_csv(csv_content: str) -> List[TransactionRecord]:
    """
    EXTRACTION LOGIC:
    - Reads raw CSV data from external system (Revolut)
    - Handles schema mapping (column detection)
    - Error handling for malformed data
    """
    f = io.StringIO(csv_content)
    reader = csv.reader(f)
    header = next(reader)
    
    # Schema validation - ensures data contract is met
    try:
        started_date_col_idx = header.index('Started Date')
        description_col_idx = header.index('Description')
        amount_col_idx = header.index('Amount')
        currency_col_idx = header.index('Currency')
    except ValueError as e:
        raise ValueError(f"Missing expected CSV column: {e}")
```

**Key ETL Concepts Demonstrated:**
- ✅ **Schema Detection** - Dynamically finds columns by name
- ✅ **Data Validation** - Checks for required fields
- ✅ **Error Handling** - Gracefully handles malformed rows
- ✅ **Data Contracts** - Enforces expected format

**DBT Parallel:** In DBT, you'd use `sources` to define external data contracts and expectations.

---

### 2. **TRANSFORM (T)** - Data Processing

#### A. Currency Normalization (`currency_converter.py`)

```python
def convert_to_eur(amount, from_currency):
    """
    TRANSFORMATION: Multi-currency normalization
    - Fetches live exchange rates from API
    - Converts all amounts to base currency (EUR)
    - Enables apples-to-apples comparison
    """
    if from_currency == 'EUR':
        return amount
    
    rates = get_exchange_rates()
    rate = rates[from_currency]
    return amount / rate  # Conversion logic
```

**Why This Matters:**
- 💡 **Data Standardization** - All financial data in same unit
- 💡 **Accurate Aggregations** - Can sum/compare different currencies
- 💡 **Business Logic** - Encapsulates calculation rules

**DBT Parallel:** This is like a DBT model that creates a `staging` layer with standardized currency columns:
```sql
-- dbt model: stg_expenses__normalized.sql
SELECT 
    expense_id,
    amount / {{ get_exchange_rate(currency) }} AS amount_eur,
    currency AS original_currency
FROM {{ source('raw', 'expenses') }}
```

---

#### B. Merchant Categorization (`merchant_mapper.py`)

```python
def auto_categorize_transaction(description, transaction_type='expenses'):
    """
    TRANSFORMATION: Dimension enrichment
    - Maps raw merchant names to standardized categories
    - Maintains lookup table (merchant_category_*.json)
    - Learns from user input (updates mappings)
    """
    merchants = load_merchant_categories(transaction_type)
    return merchants.get(description)
```

**Key Concepts:**
- 🗂️ **Master Data Management** - Centralized merchant categories
- 🗂️ **Dimension Enrichment** - Adds analytical context
- 🗂️ **Data Quality** - Ensures consistent categorization

**DBT Parallel:** This is like a DBT `dim_merchants` table joined with fact tables:
```sql
-- dbt model: dim_merchants.sql
SELECT 
    merchant_name,
    category,
    updated_at
FROM {{ ref('merchant_mappings') }}
```

---

#### C. Date Parsing & Standardization

```python
# In revolut_importer.py
date = _dt.datetime.strptime(date_str_with_time, '%Y-%m-%d %H:%M:%S').date()
```

**Why Dates Matter in Data Pipelines:**
- 📅 Time is the most common dimension in analytics
- 📅 Enables time-series analysis, trends, forecasting
- 📅 Must handle different formats (ISO, US, EU, etc.)

**DBT Parallel:** DBT has date macros for consistency:
```sql
{{ dbt_utils.date_trunc('month', 'transaction_date') }} AS transaction_month
```

---

### 3. **LOAD (L)** - Data Persistence

#### Data Manager Pattern (`models/data_manager.py`)

```python
def save(self):
    """
    LOADING LOGIC:
    - Manages transactions (ACID compliance)
    - Batches inserts for performance
    - Implements upsert pattern (delete + insert)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Clear existing data (idempotent operation)
        cursor.execute('DELETE FROM expenses WHERE user_id = ?', (self.user_id,))
        
        # Bulk insert
        for expense in self._expenses:
            cursor.execute(
                'INSERT INTO expenses (...) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, date, description, category, amount, currency)
            )
        
        conn.commit()  # ACID transaction
```

**Key Concepts:**
- ⚡ **Idempotency** - Can run multiple times safely (delete + insert)
- ⚡ **Transaction Management** - All-or-nothing writes
- ⚡ **Context Managers** - Automatic connection cleanup

**DBT Parallel:** DBT models have materialization strategies:
- `table` - Full refresh (like your delete + insert)
- `incremental` - Append/upsert new data only
- `view` - No persistence (query time)

---

## 🗄️ Data Modeling & Schema Design

### Your Data Warehouse Schema

```sql
-- DIMENSION TABLE: Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,          -- Surrogate key
    username TEXT UNIQUE NOT NULL,   -- Business key
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FACT TABLE: Expenses (Transactional)
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,        -- Foreign key (dimension)
    date TEXT NOT NULL,              -- Time dimension
    description TEXT,                -- Descriptive attribute
    category TEXT NOT NULL,          -- Dimension (could be separate table)
    amount REAL NOT NULL,            -- Measure
    currency TEXT DEFAULT 'EUR',     -- Currency dimension
    created_at TIMESTAMP,            -- Audit column
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- FACT TABLE: Incomes (Transactional)
CREATE TABLE incomes (
    -- Same structure as expenses
);

-- DIMENSION TABLE: Budgets (Reference)
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    limit_amount REAL NOT NULL,
    created_at TIMESTAMP,
    UNIQUE(user_id, category),       -- Compound business key
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Schema Design Concepts

#### 1. **Star Schema** (Fact + Dimensions)

Your project follows a **star schema** pattern:

```
         ┌─────────┐
         │  users  │ (Dimension)
         └────┬────┘
              │
         ┌────┴─────────────┐
         │                  │
    ┌────▼────┐       ┌────▼────┐
    │ expenses│       │ incomes │ (Fact Tables)
    └────┬────┘       └────┬────┘
         │                 │
         └────┬────────────┘
              │
         ┌────▼────┐
         │ budgets │ (Dimension)
         └─────────┘
```

- **Fact Tables** (expenses, incomes): Store measurable events (transactions)
- **Dimension Tables** (users, budgets): Store descriptive attributes

**DBT Parallel:** DBT organizes models into `staging`, `intermediate`, and `marts` layers:
```
models/
  staging/
    stg_expenses.sql          # Clean raw data
    stg_incomes.sql
  intermediate/
    int_expenses__normalized.sql  # Business logic
  marts/
    finance/
      fct_transactions.sql    # Final fact table
      dim_categories.sql      # Final dimension
```

---

#### 2. **Slowly Changing Dimensions (SCD)**

Your merchant categories demonstrate **SCD Type 1** (overwrite):

```python
def update_merchant_category(merchant_name, category, transaction_type='expenses'):
    """
    SCD Type 1: Overwrites existing mapping
    - No history tracking
    - Simpler, but loses audit trail
    """
    merchants = load_merchant_categories(transaction_type)
    merchants[merchant_name] = category  # Overwrites
    save_merchant_categories(merchants, transaction_type)
```

**In a production DWH**, you might implement **SCD Type 2** (versioned history):
```sql
-- SCD Type 2 example (not in your project)
CREATE TABLE dim_merchants (
    merchant_key INTEGER PRIMARY KEY,
    merchant_name TEXT,
    category TEXT,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);
```

**DBT has SCD macros:**
```sql
{{ snapshot_scd2('merchants', updated_at, 'merchant_name') }}
```

---

#### 3. **Denormalization for Analytics**

Notice how `category` is stored directly in `expenses` table:

```sql
-- Normalized approach (more tables, more joins)
expenses → expense_categories → categories

-- Denormalized approach (what you use)
expenses (includes category column directly)
```

**Why Denormalize?**
- ✅ Faster queries (no joins needed)
- ✅ Simpler SQL for analysts
- ❌ More storage space
- ❌ Update anomalies

**DBT Best Practice:** Create materialized views with denormalized data for analytics:
```sql
-- dbt model: fct_expense_analysis.sql
SELECT 
    e.*,
    u.username,
    c.category_name,
    c.category_group
FROM {{ ref('stg_expenses') }} e
LEFT JOIN {{ ref('dim_users') }} u USING (user_id)
LEFT JOIN {{ ref('dim_categories') }} c USING (category_id)
```

---

## ✅ Data Quality & Governance

### Data Quality Checks in Your Project

#### 1. **Schema Validation** (revolut_importer.py)

```python
try:
    started_date_col_idx = header.index('Started Date')
    description_col_idx = header.index('Description')
    # ...
except ValueError as e:
    raise ValueError(f"Missing expected CSV column: {e}")
```

**DBT Equivalent:**
```yaml
# schema.yml
sources:
  - name: revolut
    tables:
      - name: transactions
        columns:
          - name: started_date
            tests:
              - not_null
          - name: amount
            tests:
              - not_null
```

---

#### 2. **Type Checking & Coercion**

```python
try:
    amount = float(amount_str)
    date = _dt.datetime.strptime(date_str_with_time, '%Y-%m-%d %H:%M:%S').date()
except (ValueError, IndexError) as e:
    print(f"Skipping malformed row: {row} - Error: {e}")
    continue  # Skip bad data
```

**Data Quality Principles:**
- 🛡️ **Fail Gracefully** - Log errors but continue processing
- 🛡️ **Type Safety** - Explicit conversions (str → float, str → date)
- 🛡️ **Auditing** - Track skipped rows for investigation

**DBT Tests:**
```yaml
models:
  - name: stg_expenses
    columns:
      - name: amount
        tests:
          - not_null
          - positive_amount  # Custom test
      - name: transaction_date
        tests:
          - not_null
          - date_format_check
```

---

#### 3. **Referential Integrity** (Foreign Keys)

```sql
CREATE TABLE expenses (
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Ensures:**
- No orphaned records (expenses without users)
- Data consistency across tables

**DBT Tests:**
```yaml
- name: user_id
  tests:
    - relationships:
        to: ref('dim_users')
        field: user_id
```

---

#### 4. **Data Freshness**

Your project uses `created_at` timestamps:

```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Why Track Timestamps?**
- 🕒 Monitor data pipeline health
- 🕒 Detect stale data
- 🕒 Audit trail for compliance

**DBT Freshness Checks:**
```yaml
sources:
  - name: revolut
    loaded_at_field: created_at
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
```

---

#### 5. **Idempotency** (Run Multiple Times Safely)

```python
# Delete existing data before inserting
cursor.execute('DELETE FROM expenses WHERE user_id = ?', (self.user_id,))

# Then insert fresh data
for expense in self._expenses:
    cursor.execute('INSERT INTO expenses (...) VALUES (...)')
```

**Idempotency = Key Data Engineering Principle:**
- Running pipeline twice produces same result
- No duplicate data
- Enables safe retries after failures

**DBT Handles This Automatically:**
```sql
-- DBT creates/replaces tables atomically
{{ config(materialized='table') }}
```

---

## 🔧 How This Relates to DBT & Data Warehousing

### Your Project → DBT Translation Guide

| **Your Component** | **DBT Equivalent** | **Purpose** |
|-------------------|-------------------|------------|
| `revolut_importer.py` | `sources.yml` | Define external data sources |
| `currency_converter.py` | `macros/convert_currency.sql` | Reusable transformation logic |
| `merchant_mapper.py` | `seed/merchant_categories.csv` + `ref()` | Lookup table management |
| `database.py` table creation | `schema.yml` + `dbt run` | Data modeling & DDL |
| `data_manager.py` | DBT models with materializations | Orchestration layer |
| Manual transformations in app.py | `models/marts/*.sql` | Analytics business logic |
| SQLite database | Cloud DWH (Snowflake, BigQuery, Redshift) | Storage layer |

---

### What You'd Build in DBT

If you were to **rebuild this project in DBT**, your structure would look like:

```
dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_revolut__transactions.sql     # Extract & clean CSV
│   │   └── stg_exchange_rates.sql            # API data
│   ├── intermediate/
│   │   ├── int_expenses__normalized.sql      # Currency conversion
│   │   ├── int_expenses__categorized.sql     # Merchant mapping
│   │   └── int_transactions__unified.sql     # Combine income/expenses
│   └── marts/
│       └── finance/
│           ├── fct_transactions.sql          # Final fact table
│           ├── dim_categories.sql            # Categories dimension
│           └── agg_monthly_summary.sql       # Pre-aggregated metrics
│
├── seeds/
│   └── merchant_categories.csv               # Lookup data
│
├── macros/
│   ├── convert_currency.sql                  # Reusable function
│   └── categorize_merchant.sql
│
├── tests/
│   └── assert_positive_amounts.sql           # Data quality test
│
└── dbt_project.yml
```

---

### Example DBT Model (Your Logic Translated)

**Your Python Code:**
```python
def convert_to_eur(amount, from_currency):
    rates = get_exchange_rates()
    return amount / rates[from_currency]
```

**DBT SQL Model:**
```sql
-- models/intermediate/int_expenses__normalized.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'expenses') }}
),

exchange_rates AS (
    SELECT * FROM {{ ref('stg_exchange_rates') }}
),

converted AS (
    SELECT 
        s.expense_id,
        s.user_id,
        s.date,
        s.description,
        s.category,
        s.amount AS original_amount,
        s.currency AS original_currency,
        
        -- Currency conversion logic
        CASE 
            WHEN s.currency = 'EUR' THEN s.amount
            ELSE s.amount / er.rate_to_eur
        END AS amount_eur
        
    FROM source s
    LEFT JOIN exchange_rates er 
        ON s.currency = er.currency
        AND s.date = er.rate_date
)

SELECT * FROM converted
```

**Key DBT Concepts:**
- `{{ source() }}` - References external data
- `{{ ref() }}` - References other DBT models (creates dependency graph)
- Automatic dependency resolution
- Incremental processing
- Testing framework
- Documentation generation

---

## 🎤 Key Learnings for Your Interview

### 1. **Talk About ETL Design Patterns**

**What to Say:**
> "In my budget tracker project, I implemented a complete ETL pipeline. For **extraction**, I built a CSV parser that validates schema contracts before processing. For **transformation**, I implemented currency normalization to enable cross-currency analytics—all amounts are converted to a base currency (EUR) using live exchange rates. I also built a merchant categorization system that enriches raw transaction descriptions with standardized categories. For **loading**, I used a transaction-based approach with idempotent writes to ensure data consistency."

**Why This Impresses:**
- Shows you understand E-T-L components
- Demonstrates real implementation experience
- Mentions data quality (schema validation)
- Uses professional terminology (idempotent, schema contracts)

---

### 2. **Explain Data Modeling Choices**

**What to Say:**
> "I designed the database using a **star schema** with fact tables for transactions (expenses/incomes) and dimension tables for users and budgets. I chose to denormalize the category field directly into the fact table rather than creating a separate dimension because query performance was more important than normalization for this analytical use case. I also implemented foreign key constraints to maintain referential integrity."

**Why This Impresses:**
- Shows you know dimensional modeling
- Explains trade-offs (denormalization vs performance)
- Demonstrates awareness of analytics best practices

---

### 3. **Discuss Data Quality Measures**

**What to Say:**
> "I implemented several data quality checks: schema validation to ensure all required CSV columns exist, type coercion with error handling to skip malformed rows, and referential integrity via foreign keys. I also made the load process idempotent—using a delete-then-insert pattern—so the pipeline can be safely re-run without creating duplicates. Every record has an audit timestamp for tracking data freshness."

**Why This Impresses:**
- Shows you think about data reliability
- Mentions specific techniques (idempotency, referential integrity)
- Demonstrates production-ready thinking

---

### 4. **Connect to DBT Concepts**

**What to Say:**
> "While my project uses Python for transformations, I understand that DBT does this in SQL as code. My currency converter function would become a DBT macro, my merchant mappings would be seed files, and my data pipeline steps would be modeled as staging → intermediate → marts layers. The delete-insert pattern I used is similar to DBT's table materialization strategy."

**Why This Impresses:**
- Shows you researched the internship's tech stack
- Demonstrates ability to translate concepts across tools
- Proves you're ready to learn DBT quickly

---

### 5. **Highlight Migration/Refactoring Experience**

**What to Say:**
> "I actually performed a schema migration when I added currency support to the project. I had to alter existing tables to add a currency column, provide default values, and update all transformation logic to handle multi-currency data. This required careful planning to avoid breaking existing functionality—similar to the DBT refactoring work mentioned in the internship description."

**Why This Impresses:**
- Directly relates to "refactoring existing DWH code to DBT"
- Shows you understand backward compatibility challenges
- Demonstrates real-world migration experience

---

### 6. **Describe Analytics Use Cases**

**What to Say:**
> "The pipeline powers several analytical use cases: a dashboard with KPIs like total income/expenses and balance trends, category-based spending analysis with aggregations, time-series analysis for monthly trends, and budget vs. actual comparisons. I implemented statistical functions like linear regression for forecasting. All of this required properly modeled data with consistent time dimensions and normalized measures."

**Why This Impresses:**
- Shows you understand analytics requirements drive data modeling
- Mentions business outcomes, not just technical implementation
- Demonstrates end-to-end thinking

---

## 🎯 Practice Interview Questions & Answers

### Q: "What is ETL and can you give an example?"

**Your Answer:**
> "ETL stands for Extract, Transform, Load—the process of moving data from source systems into a data warehouse. In my budget tracker, I built an ETL pipeline for Revolut bank statements. 
> 
> **Extract:** I parse CSV files and validate the schema. 
> **Transform:** I convert all currencies to EUR using live exchange rates and categorize merchants. 
> **Load:** I write the transformed data to a SQLite database using transactional writes.
>
> I made it idempotent so we can re-run it safely if something fails."

---

### Q: "What's the difference between a fact table and a dimension table?"

**Your Answer:**
> "Fact tables store measurable events—like transactions—with foreign keys to dimensions. Dimension tables store descriptive attributes.
>
> In my project:
> - **Fact tables:** expenses and incomes (store transaction amounts, dates)
> - **Dimension tables:** users and budgets (store who and what)
>
> This star schema design makes analytics queries faster because you don't need complex joins."

---

### Q: "How do you ensure data quality in a pipeline?"

**Your Answer:**
> "I use multiple strategies:
> 1. **Schema validation** - Check that CSV files have expected columns
> 2. **Type checking** - Convert strings to numbers/dates with error handling
> 3. **Referential integrity** - Use foreign keys to prevent orphaned records
> 4. **Idempotency** - Use delete-insert pattern so re-runs don't create duplicates
> 5. **Audit trails** - Track created_at timestamps for freshness monitoring
>
> In DBT, these would be implemented as tests in schema.yml files."

---

### Q: "Tell me about a time you had to migrate or refactor data structures."

**Your Answer:**
> "I added multi-currency support to my budget tracker. Originally, everything was in EUR. I had to:
> 1. Alter tables to add a currency column
> 2. Backfill existing data with default 'EUR' values
> 3. Update all transformation logic to handle currency conversion
> 4. Ensure backward compatibility with existing records
>
> This taught me the importance of careful migration planning and testing—exactly like refactoring a DWH to DBT."

---

### Q: "What interests you about DBT specifically?"

**Your Answer:**
> "I'm excited about DBT because it brings software engineering best practices to analytics. My Python transformations work, but they're not easily testable or versionable. DBT's approach of 'analytics as code' with built-in testing, documentation, and lineage tracking is exactly what modern data teams need. I also love that it creates a dependency graph automatically—in my project, I have to manually manage the order of transformations."

---

## 📚 Key Terminology to Use in Interviews

| **Term** | **Definition** | **Where It Appears in Your Project** |
|---------|---------------|-------------------------------------|
| **ETL** | Extract, Transform, Load | Your entire data pipeline |
| **Star Schema** | Fact + dimension tables | Your database design |
| **Idempotency** | Safe to run multiple times | Your delete-insert pattern |
| **Data Lineage** | Tracking data flow | Transformations from CSV → DB |
| **Dimensional Modeling** | Organizing data for analytics | Fact vs dimension tables |
| **Data Mart** | Subject-specific data subset | Your expense/income domains |
| **Staging Layer** | Cleaned raw data | Your initial CSV parse |
| **Business Logic** | Domain-specific rules | Currency conversion, categorization |
| **Data Contract** | Expected data format | CSV column validation |
| **Referential Integrity** | Valid foreign keys | user_id relationships |
| **Denormalization** | Flattening for performance | Category stored in expenses |
| **SCD** (Slowly Changing Dimension) | Tracking dimension changes | Merchant category updates |

---

## 🚀 How to Improve Your Project Before Interview

### Quick Wins to Demonstrate Data Engineering Skills:

1. **Add a `README` section** explaining the data pipeline architecture (use diagrams from this tutorial)

2. **Create a data dictionary** documenting all tables and columns

3. **Add data quality metrics**:
   ```python
   def calculate_data_quality_score():
       total_transactions = len(expenses)
       categorized = len([e for e in expenses if e.category != 'Other'])
       return (categorized / total_transactions) * 100
   ```

4. **Implement incremental loading** instead of full refresh:
   ```python
   # Load only new transactions since last run
   last_loaded_date = get_max_date_from_db()
   new_transactions = [t for t in transactions if t.date > last_loaded_date]
   ```

5. **Add logging** to track pipeline execution:
   ```python
   import logging
   logging.info(f"Extracted {len(transactions)} transactions")
   logging.info(f"Converted {converted_count} currencies")
   ```

6. **Create a simple orchestration script**:
   ```python
   def run_pipeline():
       extract_data()
       transform_data()
       validate_data()
       load_data()
       generate_reports()
   ```

---

## 🎓 Final Tips for Your Interview

### Do's:
- ✅ Use proper terminology (ETL, star schema, idempotent)
- ✅ Explain trade-offs in your design decisions
- ✅ Connect your project to DBT concepts
- ✅ Mention data quality and testing
- ✅ Be honest about what you'd improve

### Don'ts:
- ❌ Don't say "I just followed a tutorial"
- ❌ Don't ignore data quality aspects
- ❌ Don't claim expertise in DBT if you haven't used it
- ❌ Don't forget to mention the business value

### Key Message to Convey:
> "While I haven't used DBT yet, I've built a complete data pipeline from scratch that demonstrates ETL principles, data modeling, and quality controls. I understand how my transformations would translate to DBT's SQL-based approach, and I'm excited to learn the tool that's become the industry standard for analytics engineering."

---

## 📊 Bonus: Draw This Architecture in Interview

If you have a whiteboard, draw this flow:

```
┌─────────────┐
│ Revolut CSV │ (Source)
└──────┬──────┘
       │ Extract (parse_csv)
┌──────▼──────┐
│ Raw Records │ (Staging)
└──────┬──────┘
       │ Transform (convert_to_eur + categorize)
┌──────▼──────┐
│ Normalized  │ (Intermediate)
└──────┬──────┘
       │ Load (data_manager.save)
┌──────▼──────┐
│ SQLite DWH  │ (Data Warehouse)
└──────┬──────┘
       │ Aggregate (app.py business logic)
┌──────▼──────┐
│  Dashboard  │ (Analytics)
└─────────────┘
```

Explain: "This is my ETL pipeline. If I were using DBT, stages 1-4 would be DBT models, and stage 5 would be BI tools like Looker or Tableau."

---

## 🎉 You're Ready!

You have a **real data engineering project** with:
- ✅ Complete ETL pipeline
- ✅ Proper data modeling
- ✅ Data quality measures
- ✅ Analytics use cases
- ✅ Real-world migrations

**You're not just applying with a portfolio project—you're applying with production-ready data engineering experience.**

Good luck with your internship! 🚀
