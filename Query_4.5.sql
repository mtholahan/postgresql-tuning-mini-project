-- Query 5: Identifies conferences with 'June' in the title and more than 100 associated publications.
-- Performed well with existing indexes; no new indexing was necessary.

EXPLAIN ANALYZE
WITH june_conferences AS (
    SELECT booktitle, year
    FROM proceedings
    WHERE LOWER(title) LIKE '%june%'
    
    UNION

    SELECT booktitle, year
    FROM inproceedings
    WHERE LOWER(title) LIKE '%june%'
),
all_conference_pubs AS (
    SELECT booktitle, year FROM proceedings
    UNION ALL
    SELECT booktitle, year FROM inproceedings
)
SELECT acp.booktitle, acp.year, COUNT(*) AS publication_count
FROM all_conference_pubs acp
JOIN june_conferences jc
  ON acp.booktitle = jc.booktitle AND acp.year = jc.year
GROUP BY acp.booktitle, acp.year
HAVING COUNT(*) > 100
ORDER BY publication_count DESC;
