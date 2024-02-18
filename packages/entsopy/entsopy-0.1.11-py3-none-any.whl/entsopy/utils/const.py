"""
This module contains the file paths and API endpoint used in the entsopy package.
"""

DIRS = {
    "log": "std.log",
    "areas_control_area": "../data/areas/controlArea.json",
    "areas_bidding_zone": "../data/areas/biddingZone.json",
    "areas_border_bidding_zone": "../data/areas/borderBiddingZone.json",
    "areas_border_market_balancing_area": "../data/areas/borderMarketBalancingArea.json",
    "articles_balancing": "../data/articles/balancing.articles.json",
    "articles_generation": "../data/articles/generation.articles.json",
    "articles_load": "../data/articles/load.articles.json",
    "articles_ncm": "../data/articles/ncm.articles.json",
    "articles_outages": "../data/articles/outages.articles.json",
    "articles_transmission": "../data/articles/transmission.articles.json",
    "type_attributes": "../data/types/attributes.json",
    "type_auctions_type": "../data/types/auctions_type.json",
    "type_auctions_category": "../data/types/auctions_category.json",
    "type_directions": "../data/types/directions.json",
    "type_domains": "../data/types/domains.json",
    "type_market_agreement_contract": "../data/types/type_market_agreement.contract.json",
    "type_market_agreement_type": "../data/types/type_market_agreement.type.json",
    "type_psrtypes": "../data/types/psrtypes.json",
    "type_docstatus": "../data/types/docstatus.json",
    "type_market_product": "../data/types/market_product.json"
}

API_ENDPOINT = "https://web-api.tp.entsoe.eu/api?"