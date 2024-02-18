from typing import Optional, Any

from secodadk.models import Resource, InternalLineage
from secodadk.strats.config import (
    get_ingest_resources_strategy,
    get_network_call_strategy,
)


def declare_resource(resource: Resource):
    get_ingest_resources_strategy().declare_resource(resource)


def declare_internal_lineage(lineage: InternalLineage):
    get_ingest_resources_strategy().declare_internal_lineage(lineage)


def http_get(
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    follow_redirects: bool = False,
    verify: bool | str = True,
):
    return get_network_call_strategy().make_request(
        "GET",
        url,
        params=params,
        headers=headers,
        follow_redirects=follow_redirects,
        verify=verify,
    )


def http_post(
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[Any] = None,
    follow_redirects: bool = False,
    verify: bool | str = True,
):
    return get_network_call_strategy().make_request(
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
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[Any] = None,
    follow_redirects: bool = False,
    verify: bool | str = True,
):
    return get_network_call_strategy().make_request(
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
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[Any] = None,
    follow_redirects: bool = False,
    verify: bool | str = True,
):
    return get_network_call_strategy().make_request(
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
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[Any] = None,
    follow_redirects: bool = False,
    verify: bool | str = True,
):
    return get_network_call_strategy().make_request(
        "DELETE",
        url,
        params=params,
        headers=headers,
        data=data,
        json=json,
        follow_redirects=follow_redirects,
        verify=verify,
    )
