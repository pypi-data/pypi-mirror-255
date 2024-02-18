import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from html2text import HTML2Text

from shandryll_reader.entities import Article, ArticleSummary

URL = "https://www.treinaweb.com.br/blog/"


def get_articles() -> list[ArticleSummary]:
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    result = soup.select("section.home-artigos > div.mid > ul > li")
    return [
        ArticleSummary(
            __get_article_summary_title(article),
            __get_article_summary_slug(article),
        )
        for article in result
    ]


def get_article(slug: str) -> Article:
    response = requests.get(f"{URL}{slug}")
    soup = BeautifulSoup(response.text, "html.parser")

    return Article(
        __get_article_title(soup),
        __get_article_author(soup),
        __get_article_content(soup),
    )


def __get_article_title(soup: BeautifulSoup) -> str:
    return str(soup.select_one("h1").text).strip()


def __get_article_author(soup: BeautifulSoup) -> str:
    return str(soup.select_one("span.dot-separator > a").attrs["title"]).strip()


def __get_article_content(soup: BeautifulSoup) -> str:
    h = HTML2Text()
    html_content = str(soup.select_one("article"))
    return h.handle(html_content)


def __get_article_summary_title(article: Tag) -> str:
    return str(article.select_one("h5 > a").text).strip()


def __get_article_summary_slug(article: Tag) -> str:
    return str(article.select_one("h5 > a")["href"].split("/")[-1]).strip()
