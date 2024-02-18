from secodadk.strats.core import IngestResourcesStrategy, NetworkCallStrategy
from secodadk.strats.default import (
    DefaultNetworkCallStrategy,
    DefaultIngestResourcesStrategy,
)


class Config:
    def __init__(
        self,
        *,
        ingest_resources_strategy: IngestResourcesStrategy,
        network_call_strategy: NetworkCallStrategy,
    ):
        self.ingest_resources_strategy = ingest_resources_strategy
        self.network_call_strategy = network_call_strategy


config = Config(
    ingest_resources_strategy=DefaultIngestResourcesStrategy(),
    network_call_strategy=DefaultNetworkCallStrategy(),
)


def set_ingest_resource_strategy(new_strategy: IngestResourcesStrategy):
    config.ingest_resources_strategy = new_strategy


def set_network_call_strategy(new_strategy: NetworkCallStrategy):
    config.network_call_strategy = new_strategy


def get_ingest_resources_strategy():
    return config.ingest_resources_strategy


def get_network_call_strategy():
    return config.network_call_strategy
