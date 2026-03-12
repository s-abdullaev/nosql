
-- ============================================================
-- Full-Text Search Examples
-- ============================================================

-- 1. Basic: convert text to tsvector and search with tsquery
SELECT id, title
FROM article
WHERE to_tsvector('english', body) @@ to_tsquery('english', 'PostgreSQL & search');

-- 2. Combine title + body for a richer search vector
SELECT id, title
FROM article
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'database & index');

-- 3. Rank results by relevance
SELECT id, title,
       ts_rank(to_tsvector('english', body), to_tsquery('english', 'renewable & energy')) AS rank
FROM article
WHERE to_tsvector('english', body) @@ to_tsquery('english', 'renewable & energy')
ORDER BY rank DESC;

-- 4. Use plainto_tsquery for natural-language input (no operators needed)
SELECT id, title
FROM article
WHERE to_tsvector('english', body) @@ plainto_tsquery('english', 'memory safety garbage collector');

-- 5. Use websearch_to_tsquery for Google-like syntax ("quotes", OR, -)
SELECT id, title
FROM article
WHERE to_tsvector('english', body) @@ websearch_to_tsquery('english', '"graph databases" OR Neo4j');

-- 6. Highlight matching fragments with ts_headline
SELECT id, title,
       ts_headline('english', body,
                   plainto_tsquery('english', 'remote work productivity'),
                   'StartSel=**, StopSel=**, MaxFragments=2, FragmentDelimiter= ... ') AS snippet
FROM article
WHERE to_tsvector('english', body) @@ plainto_tsquery('english', 'remote work productivity');

-- 7. Create a stored tsvector column + GIN index for fast lookups
-- ALTER TABLE article ADD COLUMN search_vector tsvector
--     GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || body)) STORED;

-- CREATE INDEX idx_article_search ON article USING GIN (search_vector);

-- Now queries can use the indexed column directly
SELECT id, title
FROM article
WHERE search_vector @@ websearch_to_tsquery('english', 'artificial intelligence healthcare');

-- 8. Phrase search (words must appear adjacent)
SELECT id, title
FROM article
WHERE search_vector @@ phraseto_tsquery('english', 'full text search');