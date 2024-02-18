"""
This module contains the file paths and API endpoint used in the entsopy package.
"""

DIRS = {
    "log": "entsopy/data/logs/std.log",
    "areas_control_area": "entsopy/data/areas/controlArea.json",
    "areas_bidding_zone": "entsopy/data/areas/biddingZone.json",
    "areas_border_bidding_zone": "entsopy/data/areas/borderBiddingZone.json",
    "areas_border_market_balancing_area": "entsopy/data/areas/borderMarketBalancingArea.json",
    "articles_balancing": "entsopy/data/articles/balancing.articles.json",
    "articles_generation": "entsopy/data/articles/generation.articles.json",
    "articles_load": "entsopy/data/articles/load.articles.json",
    "articles_ncm": "entsopy/data/articles/ncm.articles.json",
    "articles_outages": "entsopy/data/articles/outages.articles.json",
    "articles_transmission": "entsopy/data/articles/transmission.articles.json",
    "type_attributes": "entsopy/data/types/attributes.json",
    "type_auctions_type": "entsopy/data/types/auctions_type.json",
    "type_auctions_category": "entsopy/data/types/auctions_category.json",
    "type_directions": "entsopy/data/types/directions.json",
    "type_domains": "entsopy/data/types/domains.json",
    "type_market_agreement_contract": "entsopy/data/types/type_market_agreement.contract.json",
    "type_market_agreement_type": "entsopy/data/types/type_market_agreement.type.json",
    "type_psrtypes": "entsopy/data/types/psrtypes.json",
    "type_docstatus": "entsopy/data/types/docstatus.json",
    "type_market_product": "entsopy/data/types/market_product.json",
}

API_ENDPOINT = "https://web-api.tp.entsoe.eu/api?"
