import abc
from typing import Optional, Any

from httpx import Response

from secodadk.ingestion_models import Resource, DeclaredLineage


class IngestResourcesStrategy(abc.ABC):
    @abc.abstractmethod
    def declare_resource(self, resource: Resource):
        ...

    @abc.abstractmethod
    def declare_lineage(self, lineage: DeclaredLineage):
        ...

    @abc.abstractmethod
    def finalize(self):
        ...


class NetworkCallStrategy(abc.ABC):
    @abc.abstractmethod
    def make_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        verify: bool | str = True,
        follow_redirects: bool = False,
    ) -> Response:
        ...

    def finalize(self):
        pass
