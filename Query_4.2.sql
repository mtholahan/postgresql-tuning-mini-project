-- Query 2: Counts total publications grouped by booktitle and year.
-- Query was performant from the outset; no optimization required.

EXPLAIN ANALYZE WITH author_paper_counts AS (
    SELECT 
        author, 
        CASE 
            WHEN booktitle = 'VLDB' THEN 'PVLDB'
            WHEN booktitle = 'SIGMOD Conference' THEN 'SIGMOD'
        END AS booktitle, 
        COUNT(*) AS paper_count
    FROM public.inproceedings
    WHERE booktitle IN ('VLDB', 'SIGMOD Conference')
    GROUP BY author, booktitle
)
SELECT author, 
       SUM(CASE WHEN booktitle = 'PVLDB' THEN paper_count ELSE 0 END) AS PVLDB_papers,
       SUM(CASE WHEN booktitle = 'SIGMOD' THEN paper_count ELSE 0 END) AS SIGMOD_papers,
       SUM(paper_count) AS total_papers
FROM author_paper_counts
WHERE author IS NOT NULL -- Remove blank authors
GROUP BY author
ORDER BY total_papers DESC, PVLDB_papers DESC, SIGMOD_papers DESC
LIMIT 20;
