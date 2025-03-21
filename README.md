# PostgreSQL Query Optimization Mini-Project

This mini-project focuses on optimizing five SQL queries using PostgreSQL. Each query targets a specific analytical use case on publication data, and optimization strategies include index creation, query refactoring, and execution plan analysis.

## 🔧 Project Overview

This project was completed as part of a SQL performance tuning exercise. The original database had **no indexes**, and queries were analyzed using `EXPLAIN ANALYZE` before and after optimization. Performance gains were achieved by creating GIN indexes, using covering indexes, leveraging bitmap scans, and pushing filters earlier in execution plans.

---

## 📂 File Structure

- `Query1.sql` – Aggregate publications by decade (excluding seasonal/special conferences)
- `Query2.sql` – Count publications per conference
- `Query3.sql` – Filter out patterns in booktitle (`ILIKE '%workshop%'`, etc.)
- `Query4.sql` – Find top 10 authors publishing on topics related to "data"
- `Query5.sql` – Identify June conferences with over 100 publications
- `Postgres_Query_Report.docx` – Full write-up including query tuning rationale, index strategy, performance comparisons, and caching effects

---

## 📈 Performance Summary

Three of the five queries were significantly improved using indexing and filter restructuring:

| Query | Execution Time (Before) | Execution Time (After) | Speedup |
|-------|--------------------------|-------------------------|---------|
| Query 1 | ~35.6 sec | ~11.6 sec | 3x faster |
| Query 3 | ~7.8 sec | ~1.6 sec | 5x faster |
| Query 4 | ~16.7 sec | ~8.1 sec | 2x faster |

Queries 2 and 5 were performant out of the box and required no additional tuning.

---

## 🧠 Optimization Techniques Used

- ✅ GIN indexes with `gin_trgm_ops` for efficient `ILIKE` and `LOWER(title)` searches
- ✅ Covering indexes to support index-only scans
- ✅ Use of `CTE`s and `UNION ALL` to streamline logic
- ✅ Index scan hints via `SET enable_seqscan = OFF` when needed
- ✅ Execution plan analysis with `EXPLAIN ANALYZE`

---

## 📌 Note

All index creation and tuning decisions are documented in the accompanying Word report. Execution times and performance insights were validated using `EXPLAIN ANALYZE` and stored in Excel for reference.

---

## 🧾 Author

**Mark Holahan**  
Data Architect | SQL Performance Enthusiast
