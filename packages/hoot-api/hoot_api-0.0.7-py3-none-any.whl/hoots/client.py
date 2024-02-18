from enum import Enum
from typing import List, Optional
import os
from typing import Union

import requests
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True


class ChannelStatus(Enum):
    CREATED = "created",
    CREATING = "creating",
    CREATION_FAILED = "creation_failed",
    CREATION_QUEUED = "creation_queued",
    DISABLED = "disabled",
    DISABLED_FAILED = "disabled_failed",
    DISABLING = "disabling",
    UPDATED = "updated",
    UPDATING = "updating",
    UPDATION_FAILED = "updation_failed",
    UPDATION_QUEUED = "updation_queued"


class ChannelType(Enum):
    FACEBOOK = "facebook"
    MICROSOFT_TEAMS = "microsoft_teams"
    TELEGRAM = "telegram"
    VIBER = "viber"


class IAccountWebhook(BaseModel):
    accountWebhookId: str
    url: str
    verificationSignature: Optional[str] = None


class IAccount(BaseModel):
    accountId: str
    name: str
    channelIds: Optional[List[str]] = None
    creationTimestampSinceEpochInMillis: Optional[int] = None
    email: Optional[str] = None
    keys: List[str]
    webhooks: List[IAccountWebhook]


class IAccountKey(BaseModel):
    accountKeyId: str
    key: str
    creationTimestampSinceEpochInMillis: Optional[int] = None
    expirationTimestampSinceEpochInMillis: Optional[int] = None
    status: str


class IFacebookConfiguration(BaseModel):
    appId: str
    appSecret: str
    pageId: str
    pageAccessToken: str
    verifyToken: str


class IMicrosoftTeamsConfiguration(BaseModel):
    botAppId: str
    botAppPassword: str
    botDisplayName: str
    clientId: str
    clientSecret: str
    resourceGroupName: str
    resourceName: str
    subscriptionId: str
    tenantId: str


class ITelegramConfiguration(BaseModel):
    authToken: str


class IViberConfiguration(BaseModel):
    authToken: str
    name: str
    avatar: str


Configuration = Union[IFacebookConfiguration, IViberConfiguration,
                      ITelegramConfiguration, IMicrosoftTeamsConfiguration]


class IChannel(BaseModel): 
    channelId: str
    channelStatus: ChannelStatus
    channelType: ChannelType
    configuration: Configuration
    name: str


class ICreateAccountRequest(BaseModel):
    email: Optional[str] = None
    isTranslateEnable: bool
    name: str
    organizationId: str


class ICreateChannelRequest(BaseModel):
    channelType: ChannelType
    configuration: Configuration
    name: str


class ICreateOrganizationRequest(BaseModel):
    name: str
    email: Optional[str] = None


class ICreateWebhookRequest(BaseModel):
    url: str


class IOrganization(BaseModel):
    organizationId: str
    name: str
    email: Optional[str] = None
    creationTimestampSinceEpochInMillis: Optional[int] = None


class IHootAccountSecret(BaseModel):
    accountId: str
    apiKey: str


class IHootClientOptions(BaseModel):
    apiUrl: Optional[str] = None
    adminSecretKey: Optional[str] = None
    accountSecret: Optional[IHootAccountSecret] = None


class ISendMessageRequest(BaseModel):
    accountId: str
    channelId: str
    activities: List[dict]


class ISendMessage(BaseModel):
    messageId: str
    channelId: str
    status: str


class IUpdateChannelRequest(BaseModel):
    configuration: Configuration


class HootClient:

    DEFAULT_REQUEST_TIMEOUT_IN_SECS = 10
    DEFAULT_API_URL = "https://api.hoots.owl.works/api"

    def __init__(self, options: Optional[IHootClientOptions] = None):
        self.api_url = HootClient.DEFAULT_API_URL
        if options and options.apiUrl:
            self.api_url = options.apiUrl
        elif os.environ.get("HOOTS_API_URL"):
            self.api_url = os.environ.get("HOOTS_API_URL")
        self.account_secret = None
        if options and options.accountSecret:
            self.account_secret = options.accountSecret
        elif os.environ.get("HOOTS_ACCOUNT_ID") and os.environ.get("HOOTS_API_KEY"):
            self.account_secret = IHootAccountSecret(
                accountId=os.environ.get("HOOTS_ACCOUNT_ID"),
                apiKey=os.environ.get("HOOTS_API_KEY"))
        self.admin_secret = None
        if options and options.adminSecretKey:
            self.admin_secret = options.adminSecretKey
        elif os.environ.get("HOOTS_ADMIN_SECRET_KEY"):
            self.admin_secret = os.environ.get("HOOTS_ADMIN_SECRET_KEY")
        if not self.account_secret and not self.admin_secret:
            raise Exception(
                "You must provide either an account secret or an admin secret key.")

    def account(self, account_id: str) -> IAccount:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.get(
            f"{self.api_url}/account/{account_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IAccount(**(response.json()["data"]))

    def account_id(self) -> Optional[str]:
        return self.account_secret.accountId if self.account_secret else None

    def api_key(self, account_id: str, api_key_id: str) -> IAccountKey:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.get(
            f"{self.api_url}/account/{account_id}/api_key/{api_key_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IAccountKey(**(response.json()["data"]))

    def channel(self, account_id: str, channel_id: str) -> IChannel:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.get(
            f"{self.api_url}/account/{account_id}/channel/{channel_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IChannel(**(response.json()["data"]))

    def create_account_webhook(
            self, account_id: str, request: ICreateWebhookRequest) -> IAccountWebhook:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.post(
            f"{self.api_url}/account/{account_id}/webhook", headers=headers, json=request.dict(),
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IAccountWebhook(**(response.json()["data"]))

    def create_channel(self, account_id: str, request: ICreateChannelRequest) -> IChannel:
        headers = self._request_headers_with_admin_secret()
        response = requests.post(
            f"{self.api_url}/account/{account_id}/channel", headers=headers, json=request.dict(),
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IChannel(**(response.json()["data"]))

    def create_api_key(self, account_id: str) -> IAccountKey:
        headers = self._request_headers_with_admin_secret()
        response = requests.post(
            f"{self.api_url}/account/{account_id}/api_key", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IAccountKey(**(response.json()["data"]))

    def remove_api_key(self, account_id: str, api_key_id: str) -> None:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        requests.delete(
            f"{self.api_url}/account/{account_id}/api_key/{api_key_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)

    def remove_channel(self, account_id: str, channel_id: str) -> None:
        headers = self._request_headers_with_admin_secret()
        requests.delete(
            f"{self.api_url}/account/{account_id}/channel/{channel_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)

    def remove_webhook(self, account_id: str, webhook_id: str) -> None:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        requests.delete(
            f"{self.api_url}/account/{account_id}/webhook/{webhook_id}", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)

    def update_admin_secret(self, admin_secret: str) -> None:
        self.admin_secret = admin_secret

    def update_account_secret(self, account_secret: IHootAccountSecret) -> None:
        self.account_secret = account_secret

    def update_channel(self, account_id: str, channel_id: str, request: IUpdateChannelRequest) -> None:
        headers = self._request_headers_with_admin_secret()
        response = requests.put(
            f"{self.api_url}/account/{account_id}/channel/{channel_id}", headers=headers, json=request.dict(),
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IChannel(**(response.json()["data"]))

    def webhook(self, account_id: str) -> IAccountWebhook:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.get(
            f"{self.api_url}/account/{account_id}/webhook", headers=headers,
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return IAccountWebhook(**(response.json()["data"]))

    def send_message(self, request: ISendMessageRequest) -> ISendMessage:
        headers = self._request_headers_with_admin_secret_or_account_api_key()
        response = requests.post(
            f"{self.api_url}/message/send", headers=headers, json=request.dict(),
            timeout=HootClient.DEFAULT_REQUEST_TIMEOUT_IN_SECS)
        return ISendMessage(**(response.json()["data"]))

    def _request_headers_with_admin_secret(self) -> dict:
        if not self.admin_secret:
            raise Exception(
                "admin secret key is required to create / remove an organization")
        return {
            "Content-Type": "application/json",
            "X-Hoot-Admin-Secret": self.admin_secret
        }

    def _request_headers_with_admin_secret_or_account_api_key(self) -> dict:
        if not self.admin_secret and not self.account_secret:
            raise Exception(
                "admin secret key or account secret is required to get an organization")
        headers = {"Content-Type": "application/json"}
        if self.admin_secret:
            headers["X-Hoot-Admin-Secret"] = self.admin_secret
        if self.account_secret:
            headers["X-Hoot-Account-Id"] = self.account_secret.accountId
            headers["X-Hoot-Api-Key"] = self.account_secret.apiKey
        return headers
