from entsopy.classes.article import Article
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json
from rich.prompt import Prompt


def extract_article(articles, article_to_extract: str) -> Article:
    for art in articles:
        if art["key"] == article_to_extract:
            return Article(article=art)


def input_article(domain: str) -> Article:
    """
    Prompts the user to select an article based on the specified domain and returns the selected article.

    Args:
        domain (str): The domain for selecting the article.

    Returns:
        Article: The selected article.
    """

    element = "article"
    if domain == "1":
        f = open(DIRS["articles_load"], "r")
    elif domain == "2":
        f = open(DIRS["articles_ncm"], "r")
    elif domain == "3":
        f = open(DIRS["articles_transmission"], "r")
    elif domain == "4":
        f = open(DIRS["articles_generation"], "r")
    elif domain == "5":
        f = open(DIRS["articles_balancing"], "r")
    elif domain == "6":
        f = open(DIRS["articles_outages"], "r")
    data = json.load(f)

    table = create_table(
        ["Article", "Code", "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    selected_article = str(
        Prompt.ask(
            f"Insert the code of the [b]{element}[/b] you want to download data from\n",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    article = extract_article(articles=data, article_to_extract=selected_article)
    return article
