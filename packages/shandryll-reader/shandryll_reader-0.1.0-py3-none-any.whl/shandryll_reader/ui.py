from shandryll_reader.entities import Article, ArticleSummary


def show_articles(articles: list[ArticleSummary]) -> None:
    print("Últimos artigos do blog da TreinaWeb:\n")
    for index, article in enumerate(articles):
        print(f"{index} - {article.title}")


def show_article(article: Article) -> None:
    print(f"# {article.title}")
    print(f"Por {article.author}\n")
    print(article.content)
