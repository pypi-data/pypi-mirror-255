from entsopy.classes.request import RequestData
from entsopy.components.article import input_article
from entsopy.components.ui import ui_article
from entsopy.utils.csv import concat_and_save_dfs
from entsopy.classes.response import ResponseData
from entsopy.classes.httpsclient import HttpsClient
from rich import print


def home(client: HttpsClient, domain: str, download_dir: str) -> str:
    """
    Executes the main flow of the program.

    Args:
        client (HttpsClient): The HTTPS client used to make requests.
        domain (str): The domain to be used for the request.

    Returns:
        str: The file name of the saved response.
    """

    article = input_article(domain=domain)
    (
        areas,
        time_interval,
        contract_market_agreement,
        direction,
        auction_type,
        docstatus,
        psrtype,
        market_product,
        registered_resource,
    ) = ui_article(article=article)

    print("[i]Generate the request...[/i]")

    request = RequestData(
        article=article,
        time_interval=time_interval,
        contract_market_agreement=contract_market_agreement,
        direction=direction,
        auction_type=auction_type,
        areas=areas,
    )
    print("[i]Sending the request...[/i]")

    data = client.multiple_requests(request=request)

    print("[i]Processing the response...[/i]")

    res = [
        (ResponseData(content, article_code=request.article.code)).df
        for content in data
    ]

    print("[i]Saving the response file...[/i]")
    file_name = concat_and_save_dfs(
        dfs=res,
        file_name=article.domain,
        suffix=article.code,
        download_dir=download_dir,
    )

    return file_name
