# Note: we will not include this as part of published secodadk

import json
from typing import Optional, Any

import httpx

from secodadk import Resource, InternalLineage
from secodadk.strats.core import IngestResourcesStrategy, NetworkCallStrategy


class JSONLIngestResourcesStrategy(IngestResourcesStrategy):
    def __init__(self, *, resources_path: str, lineages_path: str):
        # Open file for writing
        self.resources_file = open(resources_path, "w")
        self.lineages_file = open(lineages_path, "w")

    def declare_resource(self, resource: Resource):
        self.resources_file.write(json.dumps(resource.model_dump(mode="json")) + "\n")

    def declare_internal_lineage(self, lineage: InternalLineage):
        self.lineages_file.write(json.dumps(lineage.model_dump(mode="json")) + "\n")

    def finalize(self):
        self.resources_file.close()
        self.lineages_file.close()


class EgressServerNetworkCallStrategy(NetworkCallStrategy):
    def __init__(self, *, egress_server_url: str, egress_server_token: str):
        self.egress_server_url = egress_server_url
        self.egress_server_headers = {
            "Authorization": f"Bearer {egress_server_token}",
        }

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
        response = httpx.post(
            f"{self.egress_server_url}/egress/request/",
            headers=self.egress_server_headers,
            json={
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "data": data,
                "json": json,
                "follow_redirects": follow_redirects,
                "verify": verify,
            },
        )

        if response.headers.get("Egress-Error"):
            raise httpx.HTTPError(response.text)

        return response
