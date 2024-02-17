""" MS Azure utils module """


from enum import Enum
from typing import Dict, Tuple

from azure.eventgrid import EventGridPublisherClient
from azure.identity import ClientSecretCredential

#  pylint: disable-next=E0401,E0611
from pyspark.dbutils import DBUtils  # type: ignore


class DBUtilsSecrets(Enum):
    """List of dbutils.secrets' keys"""

    def __get__(self, instance, owner) -> str:
        return str(self.value)

    PRINCIPAL_CLIENT_ID = "AzureProjectServicePrincipalClientId"
    PRINCIPAL_SECRET = "AzureProjectServicePrincipalSecret"


def cached_event_grid_client(tenant_id, event_grid_topic_endpoint) -> EventGridPublisherClient:
    """Cached version of event grid client. Used in adapter"""
    dbutils = DBUtils()
    scope = _get_scope(dbutils)
    client_id: str = dbutils.secrets.get(
        scope=scope,
        key=DBUtilsSecrets.PRINCIPAL_CLIENT_ID,
    )

    client_secret: str = dbutils.secrets.get(
        scope=scope,
        key=DBUtilsSecrets.PRINCIPAL_SECRET,
    )
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    return EventGridPublisherClient(endpoint=event_grid_topic_endpoint, credential=credential)


def get_event_grid_published_client(config: Dict, dbutils: DBUtils) -> EventGridPublisherClient:
    """Returns EventGridPublisherClient for EventGridPublished

    Args:
        config (Dict): project configuration
        dbutils (DBUtils): Databricks Utilities class instance

    Returns:
        EventGridPublisherClient: EventGridPublisherClient instance
    """

    # Get Azure Active Directory tenant, service principal user id and service principal secret
    client_id, client_secret = get_client_id_and_secret(dbutils)
    tenant_id = config["logging"]["azure_ad_tenant"]

    credential = ClientSecretCredential(
        tenant_id=tenant_id,  # schwarzit tenant
        client_id=client_id,
        client_secret=client_secret,
    )

    event_grid_topic_endpoint = config["logging"]["event_grid_topic_endpoint"]

    return EventGridPublisherClient(endpoint=event_grid_topic_endpoint, credential=credential)


def _get_scope(dbutils: DBUtils):
    scopes = dbutils.secrets.listScopes()
    if not scopes or len(scopes) > 1:
        raise ValueError("DButils secret scope is missing OR there is more than one scope!")

    #  Get dbutils.secretes scope
    scope: str = scopes[0].name
    return scope


def get_client_id_and_secret(dbutils: DBUtils) -> Tuple[str, str]:
    """Obtains Azure Service Principle credentials

    Args:
        dbutils (DBUtils): Databricks Utilities class instance

    Raises:
        ValueError: When there is more than one scope or the scope is missing

    Returns:
        Tuple[str]: Azure Service Principle credentials
    """

    scope = _get_scope(dbutils)

    #  Get Azure ServicePrinciple credentials
    client_id: str = dbutils.secrets.get(
        scope=scope,
        key=DBUtilsSecrets.PRINCIPAL_CLIENT_ID,
    )

    client_secret: str = dbutils.secrets.get(
        scope=scope,
        key=DBUtilsSecrets.PRINCIPAL_SECRET,
    )

    return client_id, client_secret
