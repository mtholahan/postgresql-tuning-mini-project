-- Query 4: Finds top 10 most prolific authors in journal and conference publications containing the term 'data' in the title.
-- Optimization involved trigram GIN indexes and filtering early via CTEs.

SET enable_seqscan = OFF; SET enable_indexscan = ON; SET enable_bitmapscan = ON;

EXPLAIN ANALYZE
WITH filtered_pubs AS (
    SELECT author, COUNT(*) AS pub_count
    FROM (
        SELECT author FROM articles WHERE LOWER(title) LIKE '%data%'
        UNION ALL
        SELECT author FROM inproceedings WHERE LOWER(title) LIKE '%data%'
    ) AS pub_data
    GROUP BY author
)
SELECT a."authorName", fp.pub_count
FROM filtered_pubs fp
JOIN public.authors a ON a."authorName" = fp.author
ORDER BY fp.pub_count DESC
LIMIT 10;


