-- Query 1: Aggregates inproceedings by decade while excluding seasonal/special conferences (e.g., workshops, symposia).
-- Focus is on improving performance using covering indexes and early filtering.

SET work_mem = '500MB';

EXPLAIN ANALYZE 
WITH conference_decades AS 
(
    -- Count papers published per conference per decade
    SELECT 
        p.booktitle AS conference_name,
        (CAST(ip.year AS INTEGER) / 10) * 10 AS decade,
        COUNT(ip."inproceedingsID") AS paper_count
    FROM public.proceedings p
    JOIN public.inproceedings ip 
        ON p.booktitle = ip.booktitle
    GROUP BY p.booktitle, decade
    HAVING COUNT(ip."inproceedingsID") >= 200
)
SELECT 
    p.booktitle AS conference_name,
    p.year AS conference_year,
    c.decade,
    c.paper_count
FROM public.proceedings p
JOIN conference_decades c 
    ON p.booktitle = c.conference_name
WHERE p.year = '2018'
ORDER BY conference_name, decade;
