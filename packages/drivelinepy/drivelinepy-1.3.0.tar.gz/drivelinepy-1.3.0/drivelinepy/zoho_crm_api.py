#=================================================================
# Author: Garrett York
# Date: 2023/12/21
# Description: Class for Zoho Billings API (formerly Zoho Subscriptions)
#=================================================================

from .base_api_wrapper import BaseAPIWrapper
from datetime import datetime

class ZohoCrmAPI(BaseAPIWrapper):

    SUPPORTED_MODULES = ["Contacts","Leads"]

    # Contact id included return by default for mass users -- fields below we can modify as needed
    # pulling a single user via /Contacts/<contact_id> will return all fields
    DEFAULT_CONTACTS_MODULE_FIELDS = [
        "Email",
        "First_Name",
        "Last_Name",
        "TRAQ_Profile_URL",
        "Subscriptions_Customer_Profile"
    ]


    #-----------------------------------------------------------------
    # Method - Constructor
    #-----------------------------------------------------------------

    def __init__(self, client_id, client_secret, refresh_token, organization_id, api_iteration_limit=50, auth_url="https://accounts.zoho.com", base_url="https://www.zohoapis.com/crm/v2/", redirect_uri="www.zohoapis.com/crm"):
        super().__init__(base_url)
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.organization_id = organization_id
        self.redirect_uri = redirect_uri
        self.api_iteration_limit = api_iteration_limit # Number of times to call an API endpoint in a single function 
        self.time_of_last_refresh = None # Set in _refresh_access_token()
        self.access_token = None # Set in _refresh_access_token()
        self._refresh_access_token()

    #-----------------------------------------------------------------
    # Method - Refresh Access Token
    #-----------------------------------------------------------------

    def _refresh_access_token(self):

        """
        Refreshes the OAuth access token using the refresh token.
        
        :return: True if the access token was successfully refreshed, False otherwise.
        """

        self.logger.info("Entering _refresh_access_token()")
        self.time_of_last_refresh = datetime.now()

        path = "/oauth/v2/token" # a / at the end of the path will break things

        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'refresh_token'
        }
        headers = {}

        response = self.post(path=path, headers=headers, data=data, is_auth=True)

        #valide if response is successful, if it was return true, if not return false
        if response is None:
            self.logger.error("Failed to refresh access token - response is None")
            return False
        else:
            #if access token exists, return true
            if "access_token" in response:
                self.access_token = response["access_token"]
                self.logger.info("Access token refreshed")
                return True
            else:
                self.logger.error("Failed to refresh access token - access token does not exist in response")
                return False
    
    #-----------------------------------------------------------------
    # Method - Check Last Time Access Token Was Refreshed
    #-----------------------------------------------------------------
    
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
    
    #-----------------------------------------------------------------
    # Method - Get Headers
    #-----------------------------------------------------------------

    def _get_headers(self):
        self.logger.info("Entering _get_headers()")
        if self.check_if_access_token_needs_refreshed():
            if not self._refresh_access_token():
                return None

        headers = {
            'X-com-zoho-subscriptions-organizationid': self.organization_id,
            'Authorization': f'Zoho-oauthtoken {self.access_token}'
        }

        self.logger.info(f'Headers have been set!')
        self.logger.info("Exiting _get_headers()")
        return headers
    
    #-----------------------------------------------------------------
    # Method - Fetch Data
    #-----------------------------------------------------------------
    
    def _fetch_data(self, endpoint, initial_params, data_key, page=1):
        self.logger.info(f'Entering _fetch_data() for endpoint {endpoint}')
        all_data_list = []
        iteration = 0
        params = initial_params
        headers = self._get_headers()

        while True:
            iteration += 1
            if iteration > self.api_iteration_limit:
                self.logger.warning(f"Pagination limit of {self.api_iteration_limit} reached for {endpoint}")
                break
            # if page is none, then we are fetching a single object, so don't include page in the params
            if page is None:
                self.logger.info(f"Fetching data from {endpoint} for a single object")
            else:
                self.logger.info(f"Fetching data from {endpoint} for page {page}")
                params["page"] = page
            response = self.get(endpoint, params=params, headers=headers)

            if response is None:
                self.logger.error(f"Error fetching data from {endpoint} for page {page}. The response is None.")
                break

            if data_key in response:
                if isinstance(response[data_key], list):
                    data_count = len(response[data_key])
                    all_data_list.extend(response[data_key])
                    self.logger.info(f"Retrieved {data_count} {data_key} from page {page}")
                    if "info" in response:
                        if response["info"]["more_records"] == True:
                            page += 1
                        else:
                            self.logger.info(f"No more pages to fetch from {endpoint}")
                            break
                    else:
                        self.logger.error(f"No 'info' key found in the response for page {page}")
                        break
                elif isinstance(response[data_key], dict):
                    all_data_list.append(response[data_key])
                    self.logger.info(f"Retrieved 1 {data_key} from page {page}")
                    break
                else:
                    self.logger.error(f"Unexpected data type for {data_key} in response")
                    break               
            else:
                self.logger.error(f"No '{data_key}' key found in the response for page {page}")
                break

        self.logger.info(f"Exiting _fetch_data() with total {len(all_data_list)} {data_key} fetched")
        return all_data_list
    
    #-----------------------------------------------------------------
    # Method - Get Customer Records
    #-----------------------------------------------------------------

    def get_customer_records(self, module, customer_id=None, first_name=None, last_name=None, email=None, page=1):
        """
        Fetches customer records from the Zoho CRM API based on the specified criteria.
        :param module: The module to fetch records from.
        :param customer_id: The ID of the customer to fetch.
        :param first_name: The first name of the customer to fetch.
        :param last_name: The last name of the customer to fetch.
        :param email: The email of the customer to fetch.
        :param page: The page number to fetch.
        """
        self.logger.info("Entering get_customer_records()")

        if self.check_if_module_is_supported(module):
            endpoint = module
        else:
            self.logger.error("Invalid module provided.")
            return None
        
        params = {}
        endpoint = module
        data_key = "data"

        
        if customer_id:
            # Fetch a specific customer by ID
            endpoint += f"/{customer_id}"
        else:
            # Search for customers based on provided criteria or fetch all if no criteria
            criteria_list = []
            if first_name:
                criteria_list.append(f"(First_Name:equals:{first_name})")
            if last_name:
                criteria_list.append(f"(Last_Name:equals:{last_name})")
            if email:
                criteria_list.append(f"(Email:equals:{email})")

            if criteria_list:
                # If search criteria are provided, use the search endpoint
                endpoint += "/search"
                params['criteria'] = 'AND'.join(criteria_list)
            # If no search criteria and no customer_id, it will fetch all records
            # Use the default fields if specific fields are not provided
            params['fields'] = ','.join(self.DEFAULT_CONTACTS_MODULE_FIELDS)

        all_records = self._fetch_data(endpoint, initial_params=params, data_key=data_key, page=page)
        
        self.logger.info(f"Exiting get_customer_records() with total {len(all_records)} records fetched")
        return all_records
    
    #-----------------------------------------------------------------
    # Method - Get Supported Modules
    #-----------------------------------------------------------------

    def get_supported_modules(self):
        return self.SUPPORTED_MODULES
    
    def check_if_module_is_supported(self, module, ):
        if module in self.SUPPORTED_MODULES:
            return True
        else:
            return False