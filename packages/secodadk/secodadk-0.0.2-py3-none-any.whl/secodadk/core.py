import abc
from typing import Optional, Any

from secodadk.ingestion_models import Resource, DeclaredLineage
from secodadk.strats.core import IngestResourcesStrategy, NetworkCallStrategy
from secodadk.strats.default import (
    DefaultIngestResourcesStrategy,
    DefaultNetworkCallStrategy,
)


class SecodaIntegration(abc.ABC):
    def __init__(
        self,
        *,
        credentials: dict,
        ingest_resources_strategy: Optional[IngestResourcesStrategy] = None,
        network_call_strategy: Optional[NetworkCallStrategy] = None,
    ):
        self.credentials: dict[str, str] = credentials
        self.ingest_resources_strategy: IngestResourcesStrategy = (
            ingest_resources_strategy or DefaultIngestResourcesStrategy()
        )
        self.network_call_strategy: NetworkCallStrategy = (
            network_call_strategy or DefaultNetworkCallStrategy()
        )

    def declare_resource(self, resource: Resource):
        """
        Declare a resource to be ingested by the integration.
        The resource can be a table, a dashboard, a column, etc.
        """
        self.ingest_resources_strategy.declare_resource(resource)

    def declare_lineage(self, lineage: DeclaredLineage):
        """
        Declare a lineage between resources
        """
        self.ingest_resources_strategy.declare_lineage(lineage)

    def finalize(self):
        self.ingest_resources_strategy.finalize()
        self.network_call_strategy.finalize()

    @abc.abstractmethod
    def extract(self):
        """
        The main extraction method of the integration.
        Your integration should implement this method to extract data from the source.

        You can use the http_get, http_post, http_put, http_patch, http_delete methods to make HTTP requests,
        and the declare_resource and declare_lineage methods to declare resources and lineages.

        Those resources and lineages will be ingested into Secoda.
        """
        pass

    def start(self):
        self.extract()
        self.finalize()

    def http_get(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        return self.network_call_strategy.make_request(
            "GET",
            url,
            params=params,
            headers=headers,
            follow_redirects=follow_redirects,
            verify=verify,
        )

    def http_post(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        return self.network_call_strategy.make_request(
            "POST",
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            follow_redirects=follow_redirects,
            verify=verify,
        )

    def http_put(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        return self.network_call_strategy.make_request(
            "PUT",
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            follow_redirects=follow_redirects,
            verify=verify,
        )

    def http_patch(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        return self.network_call_strategy.make_request(
            "PATCH",
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            follow_redirects=follow_redirects,
            verify=verify,
        )

    def http_delete(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        return self.network_call_strategy.make_request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            follow_redirects=follow_redirects,
            verify=verify,
        )
