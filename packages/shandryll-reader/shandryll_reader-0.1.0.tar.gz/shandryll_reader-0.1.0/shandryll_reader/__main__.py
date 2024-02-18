import sys

from shandryll_reader import feed
from shandryll_reader.entities import ArticleSummary
from shandryll_reader.ui import show_article, show_articles

SUMMARY_ARTICLES: list[ArticleSummary] = []


def main() -> None:
    """Main entry point for the shandryll_reader package."""
    SUMMARY_ARTICLES = feed.get_articles()

    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if args:
        for article_id in args:
            article = feed.get_article(SUMMARY_ARTICLES[int(article_id)].slug)
            show_article(article)
    else:
        show_articles(SUMMARY_ARTICLES)
        sys.exit(0)


if __name__ == "__main__":
    main()
