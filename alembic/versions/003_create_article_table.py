"""Create article table with full-text search support.

Revision ID: 0003
Revises: 0002
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "article",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("author", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("published", sa.Date, nullable=False, server_default=sa.text("CURRENT_DATE")),
    )

    op.execute(
        """
        ALTER TABLE article ADD COLUMN search_vector tsvector
            GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || body)) STORED
        """
    )

    op.execute(
        "CREATE INDEX idx_article_search ON article USING GIN (search_vector)"
    )


def downgrade() -> None:
    op.drop_table("article")
