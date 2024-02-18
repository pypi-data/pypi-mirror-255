from datetime import timedelta
import requests
from requests.adapters import HTTPAdapter
import urllib3
from dataclasses import dataclass
from entsopy.classes.request import RequestData
from entsopy.classes.request import RequestData
from entsopy.utils.const import API_ENDPOINT
from entsopy.logger.logger import LOGGER
from entsopy.utils.date import split_interval, get_interval, date_diff


@dataclass
class HttpsClient:
    """
    A class representing an HTTPS client.

    Attributes:
        client (requests.Session): The HTTP client session.
        retry_policy (urllib3.Retry): The retry policy for HTTP requests.
        adapter (HTTPAdapter): The HTTP adapter for handling retries.
        security_token (str): The security token for authentication.
        api_endpoint (str): The API endpoint URL.

    Methods:
        __init__(self, security_token: str): Initializes the HttpsClient object.
        get_request(self, params: dict): Sends a GET request to the API endpoint.
        multiple_requests(self, request: RequestData) -> list: Sends multiple requests to the API endpoint.

    """

    client: requests.Session
    retry_policy: urllib3.Retry
    adapter: HTTPAdapter
    security_token: str
    api_endpoint = API_ENDPOINT

    def __init__(self, security_token: str):
        """
        Initializes the HttpsClient object.

        Args:
            security_token (str): The security token for authentication.

        """
        self.security_token = security_token
        self.client = requests.Session()
        self.retry_policy = urllib3.Retry(connect=15, backoff_factor=0.5, total=10)
        self.adapter = HTTPAdapter(max_retries=self.retry_policy)
        self.client.mount("http://", self.adapter)
        self.client.mount("https://", self.adapter)
        self.header = {
            "Content-Type": "application/xml",
            "SECURITY_TOKEN": self.security_token,
        }

    def get_request(self, params: dict):
        """
        Sends a GET request to the API endpoint.

        Args:
            params (dict): The parameters for the request.

        Returns:
            list: The response content.

        """
        params["securityToken"] = self.security_token
        response = self.client.get(url=self.api_endpoint, params=params)
        LOGGER.info(f"GET: {response.url}")
        return [response.content]

    def multiple_requests(self, request: RequestData) -> list:
        """
        Sends multiple requests to the API endpoint.

        Args:
            request (RequestData): The request data object.

        Returns:
            list: The response content.

        """
        request.params["securityToken"] = self.security_token
        res = []
        start_date, end_date = split_interval(interval=request.params["TimeInterval"])
        dates_diff = date_diff(start_date, end_date)
        delta = timedelta(days=request.article.range_limit)

        if dates_diff > delta.days:
            # count = 0
            while start_date < end_date:
                interval_starting_date = start_date
                interval_ending_date = start_date + delta
                if interval_ending_date > end_date:
                    interval_ending_date = end_date
                for i in request.areas:
                    request.set_custom_attribute_by_domain(value=i)

                    tmp_time_interval = get_interval(
                        interval_starting_date, interval_ending_date
                    )
                    request.set_custom_attribute("TimeInterval", tmp_time_interval)

                    # print(request.params)
                    response = self.client.get(
                        url=self.api_endpoint, params=request.params
                    )
                    LOGGER.info(f"MULTI-GET: {response.url}")
                    res.append(response.content)

                start_date += delta

            return res
        else:
            for i in request.areas:
                request.set_custom_attribute_by_domain(i)
                response = self.client.get(url=self.api_endpoint, params=request.params)
                LOGGER.info(f"GET: {response.url}")
                res.append(response.content)
        return res
