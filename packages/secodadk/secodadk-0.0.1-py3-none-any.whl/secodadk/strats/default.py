import json
from typing import Optional, Any

import httpx

from secodadk.models import Resource, InternalLineage
from secodadk.strats.core import IngestResourcesStrategy, NetworkCallStrategy


class DefaultIngestResourcesStrategy(IngestResourcesStrategy):
    def declare_resource(self, resource: Resource):
        print(json.dumps(resource.model_dump(mode="json")))

    def declare_internal_lineage(self, lineage: InternalLineage):
        print(json.dumps(lineage.model_dump(mode="json")))

    def finalize(self):
        pass


class DefaultNetworkCallStrategy(NetworkCallStrategy):
    def make_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Any] = None,
        follow_redirects: bool = False,
        verify: bool | str = True,
    ):
        response = httpx.request(
            method,
            url,
            params=params,
            headers=headers,
            data=data,
            json=json,
            follow_redirects=follow_redirects,
            timeout=120,
            verify=verify,
        )

        return response
