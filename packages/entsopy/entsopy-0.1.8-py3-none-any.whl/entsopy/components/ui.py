from entsopy.utils.const import *
from entsopy.components.auction import input_auction_type
from entsopy.components.docstatus import input_docstatus
from entsopy.components.marketagreement import input_market_agreement
from entsopy.classes.article import Article
from entsopy.components.areas import input_areas
from entsopy.components.dates import input_date
from entsopy.components.direction import input_direction
from rich import print
import json
from entsopy.components.marketproduct import input_market_product

from entsopy.components.psrtype import input_psrtype
from entsopy.components.registeredresource import input_registeredsource


def ui_article(article: Article):
    """
    Function to handle the user interface for an article.

    Args:
        article (Article): The article object.

    Returns:
        Tuple: A tuple containing the values for areas, time_interval, contract_market_agreement,
        direction, auction_type, docstatus, psrtype, market_product, and registered_resource.
    """

    attributes = json.load(open(DIRS["type_attributes"], "r"))
    attributes.sort(key=lambda x: x["priority"], reverse=True)

    areas = None
    time_interval = None
    contract_market_agreement = None
    direction = None
    auction_type = None
    docstatus = None
    psrtype = None
    market_product = None
    registered_resource = None

    for attribute in attributes:
        attribute = attribute["name"]
        if attribute in article.attributes and article.attributes[attribute] == 1:
            if attribute == "TimeInterval":
                time_interval = input_date(article.time_type)
            elif (
                attribute == "OutBiddingZone_Domain"
                or attribute == "BiddingZone_Domain"
                or attribute == "ControlArea_Domain"
                or attribute == "In_Domain"
                or attribute == "Out_Domain"
                or attribute == "Acquiring_Domain"
                or attribute == "Connecting_Domain"
            ):
                areas = input_areas(article.area)

            elif attribute == "Contract_MarketAgreement.Type":
                contract_market_agreement = input_market_agreement()
                direction = input_direction()

            elif attribute == "Type_MarketAgreement.Type":
                contract_market_agreement = input_market_agreement(isType=True)

            elif attribute == "Auction.Type":
                auction_type = input_auction_type()

            elif attribute == "Auction.Category":
                auction_type = input_auction_type(isCategory=True)

            elif attribute == "DocStatus":
                docstatus = input_docstatus()

            elif attribute == "PsrType":
                psrtype = input_psrtype()

            elif attribute == "Standard_MarketProduct":
                market_product = input_market_product()

            elif attribute == "Original_MarketProduct":
                market_product = input_market_product(is_standard=False)

            elif attribute == "RegisteredResource":
                registered_resource = input_registeredsource()

    return (
        areas,
        time_interval,
        contract_market_agreement,
        direction,
        auction_type,
        docstatus,
        psrtype,
        market_product,
        registered_resource,
    )
