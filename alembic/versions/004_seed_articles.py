"""Seed articles for full-text search experiments.

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO article (title, body, author, category, published) VALUES
        (
            'Introduction to PostgreSQL Full-Text Search',
            'PostgreSQL provides powerful full-text search capabilities built right into the database engine. Unlike simple LIKE or ILIKE pattern matching, full-text search understands language: it normalizes words through stemming, removes stop words, and ranks results by relevance. The two key data types are tsvector, which stores a sorted list of lexemes, and tsquery, which represents a search query. Together they form the backbone of efficient text retrieval without needing an external search engine like Elasticsearch.',
            'Alice Martin',
            'database',
            '2025-06-15'
        ),
        (
            'Understanding B-Tree and GIN Indexes',
            'Indexes are essential for database performance. A B-Tree index is the default in PostgreSQL and works well for equality and range queries on scalar values. However, when dealing with full-text search, arrays, or JSONB data, a GIN (Generalized Inverted Index) is far more appropriate. GIN indexes map each lexeme to the rows that contain it, making tsvector lookups extremely fast. Creating a GIN index on a tsvector column can speed up text search queries by orders of magnitude.',
            'Bob Chen',
            'database',
            '2025-07-02'
        ),
        (
            'Machine Learning in Healthcare',
            'Artificial intelligence and machine learning are transforming healthcare. From predicting patient outcomes to assisting radiologists in reading medical images, deep learning models are becoming indispensable tools. Natural language processing is used to extract structured information from clinical notes, while reinforcement learning helps optimize treatment plans. The challenge remains ensuring these algorithms are transparent, explainable, and free from bias.',
            'Clara Johnson',
            'technology',
            '2025-08-20'
        ),
        (
            'Climate Change and Renewable Energy',
            'The global transition to renewable energy is accelerating as the effects of climate change become more visible. Solar and wind power have reached cost parity with fossil fuels in many regions. Battery storage technology continues to improve, addressing the intermittency problem. Governments worldwide are setting ambitious carbon neutrality targets, pushing industries to adopt greener practices. However, the transition must also account for social equity and the economic impact on communities dependent on fossil fuel industries.',
            'David Park',
            'environment',
            '2025-09-10'
        ),
        (
            'The Rise of Rust in Systems Programming',
            'Rust has emerged as a serious contender in systems programming, challenging the long-standing dominance of C and C++. Its ownership model guarantees memory safety at compile time without a garbage collector. Major projects like the Linux kernel, Android, and even parts of the Windows operating system have started integrating Rust. The language also excels in concurrent programming, making data races virtually impossible. While the learning curve is steep, developers report higher confidence in the correctness of their code.',
            'Eva Li',
            'technology',
            '2025-10-05'
        ),
        (
            'Cooking with Seasonal Vegetables',
            'Eating seasonally is one of the simplest ways to improve the flavor and nutritional value of your meals. Spring brings asparagus and peas, summer offers tomatoes and zucchini, autumn is the time for squash and root vegetables, and winter highlights hearty greens like kale. Farmers markets are the best place to discover what is in season locally. A simple roasted vegetable dish with olive oil, garlic, and fresh herbs can be more satisfying than any elaborate recipe.',
            'Frank Moreau',
            'lifestyle',
            '2025-05-18'
        ),
        (
            'Exploring Graph Databases with Neo4j',
            'Relational databases struggle with deeply connected data. Graph databases like Neo4j store data as nodes and relationships, making traversal queries natural and fast. Social networks, fraud detection, recommendation engines, and knowledge graphs are classic use cases. The Cypher query language lets you express complex patterns in a readable way. Compared to recursive SQL queries, graph traversal in Neo4j is both more intuitive and significantly faster for relationship-heavy workloads.',
            'Grace Kim',
            'database',
            '2025-11-12'
        ),
        (
            'The Psychology of Remote Work',
            'Remote work has reshaped how we think about productivity, collaboration, and work-life balance. Studies show that many employees are more productive at home, yet they also report feelings of isolation and difficulty disconnecting. Effective remote teams rely on asynchronous communication, clear documentation, and intentional social interaction. Managers must shift from monitoring presence to measuring output. The hybrid model attempts to capture the best of both worlds but introduces its own scheduling and equity challenges.',
            'Henry Nguyen',
            'business',
            '2025-04-22'
        ),
        (
            'A Brief History of the Internet',
            'The internet began as ARPANET in the late 1960s, a project funded by the United States Department of Defense. It evolved through the adoption of TCP/IP in the 1980s, the invention of the World Wide Web by Tim Berners-Lee in 1989, and the explosive growth of commercial services in the 1990s. Search engines, social media, cloud computing, and mobile connectivity have each driven successive waves of transformation. Today, the internet connects billions of devices and underpins virtually every aspect of modern life.',
            'Isabel Torres',
            'technology',
            '2025-03-30'
        ),
        (
            'NoSQL vs SQL: Choosing the Right Database',
            'The choice between SQL and NoSQL databases depends on your data model, query patterns, and scalability requirements. SQL databases like PostgreSQL enforce a rigid schema and excel at complex joins and transactions. NoSQL databases such as MongoDB, Cassandra, and Redis offer flexible schemas and horizontal scaling. Document stores suit hierarchical data, key-value stores handle caching, and column-family stores power time-series analytics. In practice, many modern architectures use a polyglot persistence strategy, combining multiple database types.',
            'Alice Martin',
            'database',
            '2025-12-01'
        );
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM article")
