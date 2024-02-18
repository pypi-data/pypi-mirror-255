class ArticleSummary:
    def __init__(self, title: str, slug: str) -> None:
        self.__title = title
        self.__slug = slug

    @property
    def title(self) -> str:
        return self.__title

    @property
    def slug(self) -> str:
        return self.__slug


class Article:
    def __init__(self, title: str, author: str, content: str) -> None:
        self.__title = title
        self.__author = author
        self.__content = content

    @property
    def title(self) -> str:
        return self.__title

    @property
    def author(self) -> str:
        return self.__author

    @property
    def content(self) -> str:
        return self.__content
