# =================================================================
# Author: Diego Plata
# Date: 2023/12/19
# Description: Class for Brightpearl API
# =================================================================

from base_api_wrapper import BaseAPIWrapper
from datetime import datetime
from brightpearl_utils.helper_functions import *

class BrightpearlApi(BaseAPIWrapper):

    # -----------------------------------------------------------------
    # Method - Constructor
    # -----------------------------------------------------------------

    def __init__(self, client_id, client_secret, refresh_token, api_iteration_limit=50,
                 auth_url="https://oauth.brightpearl.com", base_url=""):
        super().__init__(base_url)
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.api_iteration_limit = api_iteration_limit  # Number of times to call an API endpoint in a single function
        self.time_of_last_refresh = None  # Set in _refresh_access_token()
        self.access_token = None  # Set in _refresh_access_token()
        self._refresh_access_token()

    # -----------------------------------------------------------------
    # Method - Refresh Access Token
    # -----------------------------------------------------------------

    def _refresh_access_token(self):

        """
        Refreshes the OAuth access token using the refresh token.

        :return: True if the access token was successfully refreshed, False otherwise.
        """

        self.logger.info("Entering _refresh_access_token()")
        self.time_of_last_refresh = datetime.now()

        path = "/token/driveline"

        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        headers = {}

        response = self.post(path=path, headers=headers, data=data, is_auth=True)

        # valid if response is successful, if it was return true, if not return false
        if response is None:
            self.logger.error("Failed to refresh access token - response is None")
            return False
        else:
            # if access token exists, return true
            if "access_token" in response:
                self.access_token = response["access_token"]
                self.base_url = f"https://{response['api_domain']}"
                self.logger.info("Access token refreshed and base url set to api domain")
                return True
            else:
                self.logger.error("Failed to refresh access token - access token does not exist in response")
                return False

    # -----------------------------------------------------------------
    # Method - Check Last Time Access Token Was Refreshed
    # -----------------------------------------------------------------

    def check_if_access_token_needs_refreshed(self):
        """
        Checks if the access token needs to be refreshed.
        return: True if the access token needs to be refreshed, False otherwise.
        """
        self.logger.info("Entering check_last_refresh()")

        time_since_last_refresh = datetime.now() - self.time_of_last_refresh

        if time_since_last_refresh.seconds > 3600:
            self.logger.info("Exiting check_last_refresh() - Token needs to be refreshed")
            return True
        else:
            self.logger.info("Exiting check_last_refresh() - Token does not need to be refreshed")
            return False

    # -----------------------------------------------------------------
    # Method - Get Headers
    # -----------------------------------------------------------------

    def _get_headers(self):
        self.logger.info("Entering _get_headers()")
        if self.check_if_access_token_needs_refreshed():
            if not self._refresh_access_token():
                return None

        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/json',
            'brightpearl-app-ref': self.client_id,
            'brightpearl-dev-ref': 'driveline1058'
        }

        self.logger.info(f'Headers have been set!')
        self.logger.info("Exiting _get_headers()")
        return headers

    def get_all_sales_orders_from_date(self, since_date, page_size):
        # TODO: add docstring documentation
        self.logger.info("Entering get_all_sales_orders()")
        endpoint = "/public-api/driveline/order-service/sales-order-search"

        result_index = 1
        today = pd.to_datetime('today').date()
        params = {
                    "createdOn": f"{since_date}T00:00/{today}T00:00",
                    "pageSize": page_size,
                    "firstResult": result_index
        }

        sales_orders = self._fetch_sales_orders_by_date(self.base_url+endpoint, params)

        return sales_orders

    def get_all_sales_orders_by_ids(self, sales_orders):
        # TODO: add docstring documentation
        self.logger.info("Entering get_all_sales_orders_by_id()")
        order_service_endpoint = "/public-api/driveline/order-service"
        sales_order_endpoint = "/public-api/driveline/order-service/sales-order"
        params = {

        }
        headers = self._get_headers()
        orders_ids = construct_sales_orders_url(sales_orders['salesOrderId'].values, self.base_url)
        uris_response = self.options(f"{self.base_url}{sales_order_endpoint}/{','.join(orders_ids)}", headers=headers)
        urls = uris_response["response"]["getUris"]
        sales_orders = self._fetch_sales_orders_by_ids(f"{self.base_url}{order_service_endpoint}", params, urls)

        return sales_orders

    def _fetch_sales_orders_by_date(self, endpoint, initial_params):
        # TODO: add docstring documentation
        self.logger.info(f'Entering _fetch_data() for endpoint {endpoint}')
        all_data_list = []
        params = initial_params
        headers = self._get_headers()
        more_pages_available = True
        while more_pages_available:
            response = self.get(endpoint, params=params, headers=headers)
            more_pages_available = response["response"]["metaData"]["morePagesAvailable"]
            data_count = response["response"]["metaData"]["resultsReturned"]
            first_index_returned = response["response"]["metaData"]["firstResult"]
            last_index_returned = response["response"]["metaData"]["lastResult"]
            self.logger.info(f"Retrieved {data_count} results from index {first_index_returned} to index {last_index_returned}")
            all_data_list.append(sales_orders_list_to_dataframe(response["response"]["results"], response["response"]["metaData"]["columns"]))
            result_index = response["response"]["metaData"]["lastResult"] + 1
            params['firstResult'] = result_index

        self.logger.info(f"Exiting _fetch_sales_orders_by_date()")
        return pd.concat(all_data_list)

    def _fetch_sales_orders_by_ids(self, endpoint, initial_params, urls):
        # TODO: add docstring documentation
        self.logger.info(f'Entering _fetch_data() for endpoint {endpoint}')
        params = initial_params
        headers = self._get_headers()
        response = [self.get(endpoint+url, params=params, headers=headers) for url in urls]
        individual_sales_orders_list = list()
        for sale_order_dictionary in response:
            individual_sales_orders_list.append(individual_sales_orders_to_dataframe(sale_order_dictionary["response"]))
        self.logger.info(f"Exiting _fetch_sales_orders_by_ids()")
        return pd.concat(individual_sales_orders_list)