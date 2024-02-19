### clickhouse-s3-etl-tools

clickhouse-s3-etl-tools is a powerful utility designed for seamless data transfers between ClickHouse clusters using the
flexibility of Amazon S3 or any S3-compatible storage as an intermediate staging area.

## Introduction

Managing and orchestrating data movement between different ClickHouse clusters can be a challenging task. The
clickhouse-s3-etl-tools service simplifies this process by acting as a bridge, enabling efficient transfers via S3
storage. This toolset is especially useful in scenarios where you need to synchronize or backup data between ClickHouse
databases or clusters with ease.

## Installation

To quickly get started with clickhouse-s3-etl-tools, you can install the package using the following:

```pip install clickhouse-s3-etl-tools```

## Utilities

The ClickHouse S3 ETL Tools consist of two main utilities:

* s3_exporter: Processes data from a ClickHouse instance and exports it to an S3 bucket.

```
s3_exporter --ch-url-source='clickhouse+native://user:password@localhost:9000/database' \
            --s3-access-key='your_s3_access_key' \
            --s3-secret-key='your_s3_secret_key' \
            --s3-path='s3://your_bucket/path/to/data' \
            --table-name='your_table' \
            --database='your_database'
```

* s3_to_clickhouse_transfer: Retrieves data from an S3 bucket and transfers it to a ClickHouse instance.

```
s3_to_clickhouse_transfer --ch-url-destination='clickhouse+native://user:password@localhost:9000/destination_database' \
                          --s3-access-key='your_s3_access_key' \
                          --s3-secret-key='your_s3_secret_key' \
                          --s3-path='s3://your_bucket/path/to/data' \
                          --table-name='your_table' \
                          --database='your_database' \
                          --database-destination='your_destination_database' \
                          --drop-destination-table-if-exists \
                          --use-s3-cluster \
                          --cluster_name='your_directive'

```

### Common Parameters (Applicable to both `s3_exporter` and `s3_to_clickhouse_transfer`):

- `--ch-url-source` (s3_exporter) / `--ch-url-destination` (s3_to_clickhouse_transfer):
    - **Description:** ClickHouse URL for either source or destination, depending on the utility.
    - **Example:** `--ch-url-source='clickhouse+native://user:password@localhost:9000/database'`

- `--s3-access-key`:
    - **Description:** Access key for the S3 bucket.
    - **Example:** `--s3-access-key='your_s3_access_key'`

- `--s3-secret-key`:
    - **Description:** Secret key for the S3 bucket.
    - **Example:** `--s3-secret-key='your_s3_secret_key'`

- `--s3-path`:
    - **Description:** Path to the data in the S3 bucket.
    - **Example:** `--s3-path='s3://your_bucket/path/to/data'`

- `--table-name`:
    - **Description:** Name of the table in ClickHouse.
    - **Example:** `--table-name='your_table'`

- `--database` (s3_exporter) / `--database-destination` (s3_to_clickhouse_transfer):
    - **Description:** Database in ClickHouse.
    - **Example:** `--database='your_database'`

- `--batch-size`:
    - **Description:** Batch size for data transfer (optional, default: `DEFAULT_VALUE_BATCH_SIZE`).
    - **Example:** `--batch-size=100`

- `--log-level`:
    - **Description:** Log level for the utility (optional, default: `DEFAULT_VALUE_LOG_LEVEL`).
    - **Example:** `--log-level='DEBUG'`

- `--drop-destination-table-if-exists` (s3_to_clickhouse_transfer only):
    - **Description:** Drop destination table if it exists.
    - **Example:** `--drop-destination-table-if-exists`

- `--use-s3-cluster` (s3_to_clickhouse_transfer only):
    - **Description:** Use S3 cluster for data transfer.
    - **Example:** `--use-s3-cluster`

- `--cluster_name` (s3_to_clickhouse_transfer only):
    - **Description:** Directive for cluster configuration (default: "").
    - **Example:** `--cluster_name='your_directive'`

### Environment Variables:

- `NUM_PARTITIONS_DROP_IN_QUERY`:
    - **Description:** Number of partitions to drop in each query.

- `MAX_TABLE_SIZE_TO_DROP_TABLE_MB`:
    - **Description:** Maximum table size (in MB) to trigger table dropping.

- `NUMB_RECONNECT_ATTEMPTS_CH`:
    - **Description:** Number of attempts to reconnect to ClickHouse.

- `MAX_PERCENTAGE_DIFF_EXTRACT`:
    - **Description:** Maximum percentage difference for extraction.

- `MAX_PERCENTAGE_DIFF_TRANSFORM`:
    - **Description:** Maximum percentage difference for transformation.

- `MAX_PARTITIONS_PER_INSERT_BLOCK`:
    - **Description:** Maximum partitions per insert block.

- `DELAY_BETWEEN_DROP_PARTITIONS_SEC`:
    - **Description:** Delay between drop partitions (in seconds).

### Example Usage with Environment Variables:

```bash
NUM_PARTITIONS_DROP_IN_QUERY=100 \
MAX_TABLE_SIZE_TO_DROP_TABLE_MB=1000 \
NUMB_RECONNECT_ATTEMPTS_CH=3 \
MAX_PERCENTAGE_DIFF_EXTRACT=1 \
MAX_PERCENTAGE_DIFF_TRANSFORM=1 \
MAX_PARTITIONS_PER_INSERT_BLOCK=500 \
DELAY_BETWEEN_DROP_PARTITIONS_SEC=10 \
s3_exporter --ch-url-source='clickhouse+native://user:password@localhost:9000/database' \
            --s3-access-key='your_s3_access_key' \
            --s3-secret-key='your_s3_secret_key' \
            --s3-path='s3://your_bucket/path/to/data' \
            --table-name='your_table' \
            --database='your_database'
```

# ClickHouse S3 ETL Tools Documentation

## File Naming Conventions

### Metadata Files

Metadata files store information about the tables and their properties. These files follow the format:

- **File Name Format:** `__metadata__[TABLE_NAME].parquet`
- **Example:** `__metadata__my_table.parquet`

### Full Table Export

Full table exports result in Parquet files containing all the data from the table. These files follow the format:

- **File Name Format:** `[TABLE_NAME]_all.parquet`
- **Example:** `my_table_all.parquet`

### Partitioned Exports

For partitioned exports, where data is saved based on specific partition keys, files are named using the following format:

- **File Name Format:** `[TABLE_NAME]{_partition_id}.parquet`
- **Example:** `my_table{123}.parquet`

Here, `{_partition_id}` is replaced with the actual partition ID.

## Exported File Contents

### Metadata File Contents

Metadata files (`__metadata__[TABLE_NAME].parquet`) typically contain the following information:

- Table schema details
- Engine type
- Partitioning key
- Total number of rows

### Full Table Export Contents

Files generated for full table exports (`[TABLE_NAME]_all.parquet`) contain the entire dataset for the specified table.

### Partitioned Export Contents

Files generated for partitioned exports (`[TABLE_NAME]{_partition_id}.parquet`) contain data specific to the identified partition.


# Dependency Tree ClickHouse

This script generates the dependency tree of ClickHouse tables and can output the result to a file or stdout. It also provides a visualization of the tree in the console.


```bash 
dependency_tree_clickhouse --ch-url <ClickHouse_URL> \
                           --databases <Databases_List> \ 
                           --file-output <Output_File> \
                          [--excluded-databases <Excluded_Databases_List>] \
                          [--log-level <Log_Level>] \ 
                          [--tables <Tables_List>]  \
                          [--ignore-validation] 
```

## Options 
- `--ch-url`:
  - **Description:** ClickHouse URL.
  - **Example:** `--ch-url='clickhouse+native://user:password@localhost:9000/database'`

- `--databases`:
  - **Description:** Databases list.
  - **Example:** `--databases='database1,database2'`

- `--file-output`:
  - **Description:** File output for dict result.
  - **Example:** `--file-output='/path/to/output_file'`

- `--excluded-databases`:
  - **Description:** A list of excluded databases for the parent dependency.
  - **Example:** `--excluded-databases='excluded_database1,excluded_database2'`

- `--log-level`:
  - **Description:** Log Level (default: INFO).
  - **Example:** `--log-level='DEBUG'`

- `--tables`:
  - **Description:** Tables list.
  - **Example:** `--tables='table1,table2'`

- `--ignore-validation`:
  - **Description:** Ignore validation after fetching data.
  - **Example:** `--ignore-validation`

### Example Dependency Tree
```bash 
Global.root
└── test.table_cascade_null
    └── test.table_cascade_amt
        └── test._trigger_table_cascade_amt
           └── test.table_cascade_view
```

In this example, the dependency tree illustrates a hierarchical relationship between ClickHouse tables. The root of the tree is Global.root, and it has child tables such as test.table_cascade_null, test.table_cascade_amt, _trigger_table_cascade_amt, and test.table_cascade_view. This structure represents the dependencies between these tables, showing how they are related to each other.