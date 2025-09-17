-- Query 3: Filters out records with specific patterns (e.g., 'workshop', 'symposium') in booktitle using ILIKE and trigram GIN indexing.
-- Optimization focused on early filter application and efficient string matching.

SET enable_indexonlyscan = OFF; SET enable_bitmapscan = OFF; SET enable_seqscan = OFF;

EXPLAIN ANALYZE
WITH filtered AS (
    SELECT year::INTEGER AS year
    FROM inproceedings
    WHERE booktitle ILIKE '%workshop%'
       OR booktitle ILIKE '%symposium%'
       OR booktitle ILIKE '%spring%'
       OR booktitle ILIKE '%fall%'
       AND year::INTEGER BETWEEN 1970 AND 2019
)
SELECT (year / 10) * 10 AS decade, COUNT(*)
FROM filtered
GROUP BY decade
ORDER BY decade;