import logging
import googleads

from .utils import GoogleServiceAccountClient


logger = logging.getLogger(__name__)


class NetworkNotFound(Exception):
    pass


class Network:
    """Network class to get network code for the given environment

    If the environment is not prod then it will create a test network if it doesn't exist

    The assumption is that the user has access to only one (prod) network
    """
    def __init__(self, application_name, env_tag, gcp_key, version="v202302", **kwargs) -> None:
        oauth2_client = GoogleServiceAccountClient(gcp_key, googleads.oauth2.GetAPIScope("ad_manager"))
        ad_manager_client = googleads.ad_manager.AdManagerClient(
            oauth2_client,
            application_name=application_name,
            **kwargs,
        )
        self.network_service = ad_manager_client.GetService("NetworkService", version=version)
        self.env_tag = env_tag
        if self.env_tag == "prod":
            self.network_code = self.get_prod_network()["networkCode"]
        else:
            try:
                test_network = self.get_test_network()
            except NetworkNotFound:
                test_network = None
            if not test_network:
                test_network = self.create_test_network()
            self.network_code = test_network["networkCode"]

    def create_test_network(self):
        """
        NOTE: this will fail with AuthenticationError.GOOGLE_ACCOUNT_ALREADY_ASSOCIATED_WITH_NETWORK
            if a test network already exists
        """
        network = self.network_service.makeTestNetwork()
        logger.debug(f"Test network created: {network}")
        return network

    def get_prod_network(self):
        networks = self.network_service.getAllNetworks()
        for network in networks:
            if not network["isTest"]:
                return network
        raise NetworkNotFound("Prod network not found")

    def get_test_network(self):
        networks = self.network_service.getAllNetworks()
        for network in networks:
            if network["isTest"]:
                return network
        raise NetworkNotFound("Test network not found")
