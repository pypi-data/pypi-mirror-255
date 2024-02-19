# Datalake CLI

This project develops a of Command Line Interface (CLI) tool designed to facilitate the migration of data from Sage ERP systems into a structured datalake and data-warehouse architecture on Google Cloud. Aimed at enhancing data management and analytics capabilities, these tools support project-specific datalake environments identified by unique tags.

## Getting Started

1. Configuration Creation:

Install the tool

```sh
pip3 install shopcloud-datalake
```

Set up your configuration directory:

```sh
mkdir config-dir
```

Create a new Datalake configuration:

```sh
datalake --project="your-google-cloud-project-id" --base-dir="config-dir" config create
```

2. Configuration Synchronization:

Sync your configuration files to the project bucket:

```sh
datalake --project="your-google-cloud-project-id" --base-dir="config-dir" config sync
```

3. Data Migration Execution:

Run the data migration process with or without specifying a table:

```sh
datalake --project="your-google-cloud-project-id" --base-dir="config-dir" run --partition-date=YYYY-MM-DD
datalake --project="your-google-cloud-project-id" --base-dir="config-dir" run <table> --partition-date=YYYY-MM-DD
```

## Architektur

```mermaid
flowchart LR
    subgraph Data-Lake
    Sage[(Sage)] --> datalake-cli
    GCS_SCHEMA[(Storage)] --> |gs://shopcloud-datalake-sage-schema| datalake-cli
    datalake-cli --> |gs://shopcloud-datalake-sage-data| GCS_DATA[(Storage)]
    end
    subgraph Data-Warehouse
    GCS_DATA[(Storage)] --> SCDS[(BigQuery)]
    end
```

## FAQs

- __Where are the configurations stored?__ Configurations are stored in a Google Cloud Storage bucket associated with each project.
- __What is the structure of the Datalake?__ Each project has a dedicated Google Cloud Project for data storage.
- __What file format is used?__ Data is stored in Parquet format for efficiency and performance.
How is data partitioned? Data is partitioned using BigQuery's TimePartitioning feature.

## Development

```sh
# run unit tests
$ python3 -m unittest
# run unit tests with coverage
$ python3 -m coverage run --source=tests,shopcloud_datalake -m unittest discover && python3 -m coverage html -d coverage_report
$ python3 -m coverage run --source=tests,shopcloud_datalake -m unittest discover && python3 -m coverage xml
```
