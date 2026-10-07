# Data Source

The dataset is provided by the German Federal Statistical Office
(Destatis / GENESIS-Online).

The original CSV file is not included in this repository.

Dataset:
12211-0001_de_flat

The ETL pipeline expects the CSV file in this directory.

# Clean Data

Dataset: **12211-0001_de_flat_clean**

created when run script when the script **02_clean_data.py** is run

# Prepare Fact Metric
Dataset: **fact_metric_ready**
created when run script when the script **03_prepare_fact_matric.py** is run

**Why do we need fact_metric_ready?**

The original Destatis file is not structured optimally for direct use in the star schema. It contains many technical columns and Destatis-specific labels.
the out file fact_metric_ready.csv ist further use to create **fact_metric** and **dimensions** the tables

# Population Fact Metric Pivot for analysis and reporting

the script **population_metric_pivot.py** create **population_metrics_pivot.csv** file

and **smart_population_metric** table.

they are analytical presentation of the data

Here, the key figures are organised in such a way that they can be compared and analysed more easily.

For example:
```text
year | gender   | age_group          | BEV036 | ERW040 | ERW041 | ERW042 | ERW043
-----|----------|--------------------|--------|--------|--------|--------|-------
2025 | männlich | 15 bis unter 20    | ...    | ...    | ...    | ...    | ...
2025 | weiblich | 15 bis unter 20    | ...    | ...    | ...    | ...    | ...
2025 | männlich | 20 bis unter 25    | ...    | ...    | ...    | ...    | ...
```

**smart_population_metric** table ist further use by **Fastapi**.

**population_metrics_pivot.csv** is table ist further use by **BI**

Here, the key figures are organised in such a way that they can be compared and analysed more easily.

