#================================================================================
# Author: Garrett York
# Date: 2024/01/31
# Description: Class for TRAQ API
#================================================================================

from .base_api_wrapper import BaseAPIWrapper

class TRAQAPI(BaseAPIWrapper):

    #---------------------------------------------------------------------------
    # Constructor
    #---------------------------------------------------------------------------

    def __init__(self, client_id, client_secret,auth_url = "https://traq.drivelinebaseball.com", base_url="https://traq.drivelinebaseball.com/"):
        super().__init__(base_url)
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.authenticate()

    #---------------------------------------------------------------------------
    # Method - Authenticate
    #---------------------------------------------------------------------------

    def authenticate(self):
        """
        Authenticates with the TRAQ API and sets the access token.
        """
        self.logger.info("Entering authenticate()")
        path = "oauth/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': '*'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self.post(path=path, data=payload, headers=headers, is_auth=True)

        if response:
            self.access_token = response.get('access_token')
            self.logger.info("Authentication successful")
        else:
            self.logger.error("Authentication failed")

        self.logger.info("Exiting authenticate()")
    
    #---------------------------------------------------------------------------
    # Method - Get Users
    #---------------------------------------------------------------------------

    def get_users(self, traq_id=None, email=None):
        """
        Retrieves user information from the TRAQ API. Prioritizes TRAQ ID over email.

        :param traq_id: TRAQ ID to filter users (optional).
        :param email: Email address to filter users (optional).
        :return: User information or list of users.
        """
        self.logger.info("Entering get_users()")

        endpoint = "api/v1.1/users"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {}

        if traq_id:
            if self.validate_traq_id(traq_id):
                params = {'id': traq_id}
            else:
                return None # Invalid TRAQ ID - logging done in validate_traq_id
        elif email:
            if self.validate_email(email):
                params = {'email': email}
            else:
                return None # Invalid email - logging done in validate_email
        else:
            self.logger.error("No filter provided for get_users()")
            return None

        response = self.get(endpoint, params=params, headers=headers)

        self.logger.info("Exiting get_users()")
        return response.get('data') if response else None

    #---------------------------------------------------------------------------
    # Method - Validate TRAQ ID
    #---------------------------------------------------------------------------

    def validate_traq_id(self, traq_id):
        """
        Validates that the TRAQ ID is a string representing a 1-6 digit integer.

        :param traq_id: The TRAQ ID to be validated.
        :return: Boolean indicating whether the ID is valid.
        """
        if isinstance(traq_id, str) and traq_id.isdigit() and 1 <= len(traq_id) <= 6:
            return True
        else:
            self.logger.error(f"Invalid TRAQ ID: {traq_id}. It must be a 1-6 digit integer.")
            return False