WITH words AS (
    SELECT 
        -- Lowercase and split text on whitespace or punctuation
        LOWER(regexp_split_to_table(contents, '[\s,.;:!?"]+')) AS word
    FROM google_file_store
)
SELECT 
    word,
    COUNT(*) AS frequency
FROM words
WHERE word <> '' -- Filter out empty matches
GROUP BY word
ORDER BY frequency DESC;
