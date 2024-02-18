# Secoda Development Kit


# Introduction
The Secoda SDK is a powerful tool for developers to create custom integrations with the Secoda platform. It provides a framework for connecting and ingesting data from various sources into Secoda, allowing for a rich and interconnected data ecosystem.

# SecodaIntegration Class

The SecodaIntegration class is an abstract base class that should be extended by any new integration. It manages authentication, network strategy, and the ingestion of resources and lineage.

When you create a custom integration by subclassing SecodaIntegration, you are required to provide a concrete implementation of the `extract` method. This method should contain the logic necessary to connect to your data source, retrieve data, and process it as needed.

# Key Methods
- `declare_resource(resource: Resource)`: Declare a resource such as a table, dashboard, or column to be ingested.
- `declare_lineage(lineage: DeclaredLineage)`: Declare a lineage, representing a relationship between two resources.


# Network Methods
- `http_get(), http_post(), http_put(), http_patch(), http_delete()`: Perform HTTP requests of various methods. These methods accept parameters for URL, query parameters, headers, and body data, along with flags for redirect following and SSL verification.

# Resource Model
Overview
The Resource model represents a resource within the Secoda platform, such as a table, column, or dashboard. 

# Lineage Models
## LineageID
LineageID represents resource(s) in your workspace, which can be either:
- A resource rom the current custom integration (InternalResource)
- A table or a column in your workspace (ExternalTable, ExternalColumn)
- Or a set of tables referenced in a SQL query (TablesFromSQLQuery)
## DeclaredLineage
### Overview
The DeclaredLineage model captures the relationship between two resources in your workspace, which can be either from the current integration or external entities.
### Attributes
- `from_identifier`: The starting point of the lineage, represented by a LineageID.
- `to_identifier`: The endpoint of the lineage, also represented by a LineageID.

## Allowed lineages types
Currently, we support the following lineage types:
- InternalResource ↔ InternalResource
- InternalResource ↔ ExternalTable
- InternalResource ↔ ExternalColumn
- ExternalTable ↔ ExternalTable
- TablesFromSQLQuery -> InternalResource
