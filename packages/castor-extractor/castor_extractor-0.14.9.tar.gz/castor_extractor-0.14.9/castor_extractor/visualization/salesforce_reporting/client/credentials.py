from typing import Dict


class SalesforceCredentials:
    """
    Class to handle Salesforce rest API permissions
    """

    def __init__(
        self,
        *,
        username: str,
        password: str,
        security_token: str,
        consumer_key: str,
        consumer_secret: str,
    ):
        self.username = username
        self.password = password + security_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def token_request_payload(self) -> Dict[str, str]:
        """
        Params to post to the API in order to retrieve the authentication token
        """
        return {
            "grant_type": "password",
            "client_id": self.consumer_key,
            "client_secret": self.consumer_secret,
            "username": self.username,
            "password": self.password,
        }
