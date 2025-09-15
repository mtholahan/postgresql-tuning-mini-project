# PostgreSQL Tuning Mini Project


## 📖 Abstract
This project focuses on query performance tuning in PostgreSQL, using a bibliographic dataset of computer science papers, authors, books, and conference proceedings. The goal was to practice query design, indexing strategies, and query plan analysis by answering a series of five analytical questions about conferences, authors, and publications.

The workflow included:

* Creating relational tables in PostgreSQL (articles, authors, books, inproceedings, proceedings, publications) and loading data from CSV extracts.

* Writing SQL queries to answer tasks such as:

*   Finding conferences with 200+ papers in a decade.

*   Identifying authors with at least 10 publications in both PVLDB and SIGMOD.

*   Summarizing conference publications by decade from 1970–2019.

*   Ranking the top authors in “data”-related venues.

*   Listing June conferences with over 100 proceedings.

* Using EXPLAIN to study execution plans, compare queries with and without indexes, and evaluate cache effects.

* Optimizing queries through indexing, improved join logic, and filtering on indexed columns.

* Writing a report analyzing performance improvements, trade-offs, and index usage.

Deliverables include individual .sql files for each query and a written report documenting how indexes improved query performance. This project strengthened my ability to design efficient SQL, interpret query plans, and optimize workloads in PostgreSQL, all essential skills for production-scale analytics.



## 🛠 Requirements
- PostgreSQL 13+ installed locally
- pgAdmin or psql CLI
- DBLP dataset of computer science publications (provided via script/CSV export)
- Python script to download and parse dataset into CSV
- GitHub repo with SQL files + written report (Word/PDF)



## 🧰 Setup
- Install PostgreSQL and pgAdmin (or use psql CLI)
- Create database: CREATE DATABASE dblp;
- Create tables: Articles, Authors, Books, Inproceedings, Proceedings, Publications
- Run Python script to download and parse DBLP XML → CSVs
- Import CSVs into corresponding Postgres tables using pgAdmin import or COPY



## 📊 Dataset
- DBLP computer science publications dataset
- Parsed into CSVs for Articles, Authors, Books, Inproceedings, Proceedings, Publications
- Imported into Postgres for query + optimization tasks



## ⏱️ Run Steps
- Write queries to answer 5 rubric questions
- Run queries without indexes; capture EXPLAIN plans
- Create indexes to optimize joins/filters
- Re-run queries with indexes; capture new EXPLAIN plans
- Document improvements in Word/PDF report



## 📈 Outputs
- 5 SQL query result sets answering rubric questions
- EXPLAIN query plans before and after indexing
- Written report comparing performance improvements



## 📸 Evidence

![query_plan_before.png](./evidence/query_plan_before.png)  
Screenshot of EXPLAIN output before index

![query_plan_after.png](./evidence/query_plan_after.png)  
Screenshot of EXPLAIN output after index

![word_report.png](./evidence/word_report.png)  
Screenshot preview of written report (full DOCX/PDF in /deliverables/)




## 📎 Deliverables

- [`- Individual SQL files for 5 rubric questions`](./deliverables/- Individual SQL files for 5 rubric questions)

- [`- Written report:`](./deliverables/- Written report:)

- [`- [Optimization Report (Word)](./deliverables/SQL_Optimization_Report.docx)`](./deliverables/- [Optimization Report (Word)](./deliverables/SQL_Optimization_Report.docx))

- [`- [Optimization Report (PDF)](./deliverables/SQL_Optimization_Report.pdf)`](./deliverables/- [Optimization Report (PDF)](./deliverables/SQL_Optimization_Report.pdf))

- [`- Raw EXPLAIN plans:`](./deliverables/- Raw EXPLAIN plans:)

- [`- /deliverables/query_plan_before.txt`](./deliverables/- /deliverables/query_plan_before.txt)

- [`- /deliverables/query_plan_after.txt`](./deliverables/- /deliverables/query_plan_after.txt)

- [`- Execution logs (if captured) in /deliverables/logs/`](./deliverables/- Execution logs (if captured) in /deliverables/logs/)




## 🛠️ Architecture
- Single-node PostgreSQL database
- DBLP dataset imported into relational schema
- Queries benchmarked with and without indexing



## 🔍 Monitoring
- Used EXPLAIN to analyze query plans
- Compared execution cost before and after indexes
- Optionally observed caching effects



## ♻️ Cleanup
- Drop dblp database if no longer needed
- Remove CSVs and parsed dataset
- Archive final Word/PDF report and SQL files in repo



*Generated automatically via Python + Jinja2 + SQL Server table `tblMiniProjectProgress` on 09-15-2025 18:04:17*