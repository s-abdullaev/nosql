from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.database import get_postgis_db
from app.models import Article
from app.schema import ArticleDetail, ArticleResult, SearchResponse

router = APIRouter(prefix="/fts", tags=["full-text search"])


class SearchMode(str, Enum):
    plain = "plain"
    websearch = "websearch"
    phrase = "phrase"
    raw = "raw"


TSQUERY_FUNCS = {
    SearchMode.plain: "plainto_tsquery",
    SearchMode.websearch: "websearch_to_tsquery",
    SearchMode.phrase: "phraseto_tsquery",
    SearchMode.raw: "to_tsquery",
}


# ── Search ───────────────────────────────────────────────────────────────────


@router.get("/search", response_model=SearchResponse)
def search_articles(
    q: str = Query(..., min_length=1, description="Search terms"),
    mode: SearchMode = Query(
        SearchMode.websearch,
        description=(
            "plain  – natural language (implicit AND); "
            "websearch – Google-like with quotes, OR, -minus; "
            "phrase – words must appear adjacent; "
            "raw – tsquery operators & | ! <->"
        ),
    ),
    db: Session = Depends(get_postgis_db),
):
    """Full-text search over articles using the GIN-indexed search_vector column."""
    tsquery_func = TSQUERY_FUNCS[mode]
    tsquery = func.cast(text(f"{tsquery_func}('english', :q)"), type_=None).params(q=q)

    query_expr = text(f"{tsquery_func}('english', :q)").bindparams(q=q)

    rank_expr = func.ts_rank(Article.search_vector, query_expr).label("rank")

    headline_expr = func.ts_headline(
        text("'english'"),
        Article.body,
        query_expr,
        text("'StartSel=<b>, StopSel=</b>, MaxFragments=2, FragmentDelimiter= … '"),
    ).label("snippet")

    query = (
        select(Article, rank_expr, headline_expr)
        .where(Article.search_vector.op("@@")(query_expr))
        .order_by(rank_expr.desc())
    )

    rows = db.execute(query).all()

    results = [
        ArticleResult(
            id=article.id,
            title=article.title,
            author=article.author,
            category=article.category,
            published=article.published.isoformat(),
            rank=round(rank, 6),
            snippet=snippet,
        )
        for article, rank, snippet in rows
    ]

    return SearchResponse(query=q, mode=mode.value, count=len(results), results=results)


# ── Article CRUD (read-only) ─────────────────────────────────────────────────


@router.get("/articles", response_model=list[ArticleDetail])
def list_articles(
    category: str | None = Query(None, description="Filter by category"),
    db: Session = Depends(get_postgis_db),
):
    """List all articles, optionally filtered by category."""
    stmt = select(Article).order_by(Article.published.desc())
    if category:
        stmt = stmt.where(Article.category == category)
    articles = db.scalars(stmt).all()
    return [
        ArticleDetail(
            id=a.id,
            title=a.title,
            body=a.body,
            author=a.author,
            category=a.category,
            published=a.published.isoformat(),
        )
        for a in articles
    ]


@router.get("/articles/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_postgis_db)):
    """Retrieve a single article by ID."""
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(404, f"Article {article_id} not found")
    return ArticleDetail(
        id=article.id,
        title=article.title,
        body=article.body,
        author=article.author,
        category=article.category,
        published=article.published.isoformat(),
    )
