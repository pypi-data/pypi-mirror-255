"""
Utils related to Google Ad manager.
"""
import google
import googleads


class GoogleServiceAccountClient(googleads.oauth2.GoogleServiceAccountClient):
    def __init__(self, info, scope, sub=None, proxy_config=None):
        self.creds = google.oauth2.service_account.Credentials.from_service_account_info(  # noqa
            info, scopes=[scope], subject=sub
        )
        self.proxy_config = (proxy_config if proxy_config else googleads.common.ProxyConfig())
        self.Refresh()
