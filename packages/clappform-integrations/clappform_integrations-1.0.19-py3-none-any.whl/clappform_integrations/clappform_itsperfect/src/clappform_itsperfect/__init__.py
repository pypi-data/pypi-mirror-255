"""ITSPerfect integration
:copyright: (c) 2023 Clappform B.V..
:license: MIT, see LICENSE for more details.
"""
__requires__ = ["requests==2.28.1", "pandas==1.5.2"]

# Metadata
__version__ = "0.0.0"
__author__ = "Clappform B.V."
__email__ = "info@clappform.com"
__license__ = "MIT"
__doc__ = "Clappform Python API wrapper"

import logging

import requests


class ItsperfectException(Exception):
    """Integration Exceptions Class"""

class Itsperfect:
    """Integration class to represent ITSPerfect API responses."""

    endpoints = [
        {
            "path":"stock",
            "key":"stock",
            "endpoint_id":"stock"
        },
        {
            "path":"purchaseOrders",
            "key":"purchaseorders",
            "endpoint_id":"purchaseorders"
        },
        {
            "path":"barcodes",
            "key":"barcodes",
            "endpoint_id":"barcodes"
        },
        {
            "path":"items",
            "key":"items",
            "endpoint_id":"items"
        },
        {
            "path":"customers",
            "key":"brands",
            "endpoint_id":"customer_brands",
            "path_extension":"brands"
        },
        {
            "path":"customers",
            "key":"addresses",
            "endpoint_id":"customer_addresses",
            "path_extension":"addresses"
        },
        {
            "path":"agents",
            "key":"agents",
            "endpoint_id":"agents"
        },
        {
            "path":"suppliers",
            "key":"suppliers",
            "endpoint_id":"suppliers"
        },
        {
            "path":"puts",
            "key":"puts",
            "endpoint_id":"puts"
        },
        {
            "path":"puts",
            "key":"items",
            "endpoint_id":"puts_items",
            "path_extension":"items"
        },
        {
            "path":"puts",
            "key":"boxes",
            "endpoint_id":"puts_boxes",
            "path_extension":"boxes"
        }
    ]

    def __init__(self, url: str, token: str, version: str = "v2", timeout: int = 5):
        """Initialize basic ITSP settings

        Args:
            url (str): base_url for the ITSP API
            token (str): Authorization token for the ITSP API.
            version (str, optional): Version of the ITSP API to be used.
                                     Defaults to "v2".
            timeout (int, optional): Timeout time for the requests made to ITSP.
                                     Defaults to 5.
        """

        self.token = token
        self.timeout = timeout
        self.base_url = f"https://{url}/api/{version}"

    def __get_endpoint(self, endpoint_id: str) -> dict:
        """Private Func to find the requested endpoint

        Args:
            endpoint_id (str): Categorical identifier for the itsp endpoint

        Returns:
            dict: Key-value pair containing all basic information on an endpoint
        """
        endpoint = next(
            (item for item in self.endpoints if item["endpoint_id"] == endpoint_id),
            None,
        )
        if endpoint is None:
            logging.error("%s not found in supported endpoints.", endpoint_id)
            raise ItsperfectException()
        return {} if endpoint is None else endpoint

    def __add_item_id(self, base_url: str, item_id: str):
        """Add item_id to the url if it is not empty
        Args:
            base_url (str): Partially parsed url
            item_id (str): Identifier for the optional ID to be sent to ITSP.
        Returns:
            str: Partially parsed url
        """

        return f"{base_url}/{item_id}" if item_id != "" else base_url

    def __add_path_extension(self, base_url: str, endpoint: dict):
        """Add path_extension to the url if it is available in the currently selected endpoint
        Args:
            base_url (str): Partially parsed url
            endpoint (dict): Key-value pair containing all basic information on an endpoint
        """
        return (
            f"{base_url}/{endpoint['path_extension']}"
            if "path_extension" in endpoint
            else base_url
        )

    def __add_token(self, base_url: str):
        """Add token to the url
        Args:
            base_url (str): Partially parsed url
        Returns:
            str: Partially parsed url
        """
        return f"{base_url}?token={self.token}"

    def __add_filter(self, base_url: str, filters: str):
        """Add custom filter to the url if it is not empty
        Args:
            base_url (str): Partially parsed url
            filters (str): Specify filters using ITSP format.
        Returns:
            str: Partially parsed url
        """
        return f"{base_url}&filter={filters}" if filters != "" else base_url

    def __get_endpoint_url(
        self, endpoint_id: str, item_id: str = "", filters: str = ""
    ) -> str:
        """Private Func to parse and return the URL for the endpoint

        Args:
            endpoint_id (str): Categorical identifier for the itsp endpoint
            item_id (str, optional): Identifier for the optional ID to be sent to ITSP.
                                     Defaults to "".
            filters (str, optional): Specify filters using ITSP format. Defaults to "".

        Returns:
            str: Partial URL containing version, token and path
                 used for a specific route call
        """

        endpoint = self.__get_endpoint(endpoint_id)

        partial_url = f"{self.base_url}/{endpoint['path']}"
        partial_url = self.__add_item_id(partial_url, item_id)
        partial_url = self.__add_path_extension(partial_url, endpoint)
        partial_url = self.__add_token(partial_url)
        partial_url = self.__add_filter(partial_url, filters)

        logging.debug("Generated URL: %s", partial_url)
        return partial_url

    def __get_endpoint_key(self, endpoint_id: str) -> str:
        """Private Func to parse and return the key for the endpoint

        Args:
            endpoint_id (str): Categorical identifier for the itsp endpoint

        Returns:
            str: The key on which ITSP will return the requested data
        """
        return self.__get_endpoint(endpoint_id)["key"]

    def __fetch_data(
        self,
        base_url: str,
        endpoint_key: str,
        batch_size: int = 100,
        page_limit: int = 0,
    ) -> list:
        """General data function to get data from itsp

        Args:
            base_url (str): Partially parsed url which contains, version,
                            path, token and filters
            endpoint_key (str): Key on which ITSP will return the requested data
            batch_size (int, optional): Specify the amount of records to
                                        be sent per request. Defaults to 100.
            page_limit (int, optional): Specify the number of iteration
                                        for the requests. Defaults to 0.

        Returns:
            list: All data collected from requested route
        """

        data = []
        page_number = 1

        def walk_pagination(page_number: int = 1):
            """Recursive function to walk through pagination
            Args:
                page_number (int, optional): Specify the page number to be requested.
                                             Defaults to 1.
            Returns:
                None
            """
            url = f"{base_url}&page={page_number}&limit={batch_size}"
            logging.debug("Pagination URL: %s", url)

            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                if (
                    "X-Pagination-Current-Page" in response.headers
                    and "X-Pagination-Page-Count" in response.headers
                ):
                    data.extend(response.json()[endpoint_key])
                else:
                    logging.error(
                        "Invalid response (url: %s) headers: %s", url, response.headers
                    )
                    raise ItsperfectException()
                # Use last page as indictor for the end of requests
                # Unless page_limit is set, in that case use page_limit
                curr_page = int(response.headers["X-Pagination-Current-Page"])
                last_page = int(response.headers["X-Pagination-Page-Count"])
                if (page_limit == 0 and curr_page < last_page) or (
                    page_limit != 0 and curr_page < page_limit
                ):
                    page_number += 1
                    walk_pagination(page_number)
            else:
                logging.error(
                    "Unable to retrieve ITSP data, %s",
                    response.text,
                )
                raise ItsperfectException()
        walk_pagination(page_number)
        return data

    def fetch_all(
        self,
        endpoint_id: str,
        batch_size: int = 100,
        page_limit: int = 0,
        filters: str = "",
    ) -> list:
        """Get all data from a single endpoint.

        Args:
            endpoint_id (str): Categorical identifier for the itsp endpoint
            batch_size (int, optional): Specify the amount of records to
                                        be sent per request. Defaults to 100.
            page_limit (int, optional): Specify the number of iteration
                                        for the requests. Defaults to 0.
            filters (str, optional): Specify filters using ITSP format. Defaults to "".

        Returns:
            list: List containing all requested data
        """

        request_url = self.__get_endpoint_url(endpoint_id=endpoint_id, filters=filters)

        endpoint_key = self.__get_endpoint_key(endpoint_id)
        return self.__fetch_data(request_url, endpoint_key, batch_size, page_limit)

    def fetch_one(self, endpoint_id: str, item_id: str, filters: str = "") -> list:
        """Returns a single record from ITSP as list with a single object

        Args:
            endpoint_id (str): Categorical identifier for the itsp endpoint
            item_id (str): Identifier for the optional ID to be sent to ITSP.
            filters (str, optional): Specify filters using ITSP format. Defaults to "".

        Returns:
            list: List containing a single record of the requested data
        """
        request_url = self.__get_endpoint_url(
            endpoint_id=endpoint_id, item_id=item_id, filters=filters
        )

        endpoint_key = self.__get_endpoint_key(endpoint_id)
        return self.__fetch_data(request_url, endpoint_key)