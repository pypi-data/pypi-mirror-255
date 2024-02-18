from dataclasses import dataclass


@dataclass
class Article:
    """
    Represents an article with its attributes.

    Attributes:
        attributes (dict): A dictionary containing the attributes of the article.
    """

    def __init__(self, article: dict):
        self.attributes = article.pop("attributes")

        for key, value in article.items():
            setattr(self, key, value)

    def __repr__(self):
        for key in self.__dict__:
            return f"Article({key}='{getattr(self, key)}')"
