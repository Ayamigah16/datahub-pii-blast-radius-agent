# DSR Checklist -- subject `subj_48213`

Source column: `cust_email`
Downstream assets evaluated: 12

- 3 action needed
- 1 no action (aggregated, not personally identifiable)
- 8 needs human review

## Action needed
- **order_details** (`urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_details,PROD)`) -- The order_details table contains customer email addresses and other PII at a row-level grain (one row per order line item), directly exposing the individual's personal data without aggregation.
- **customers** (`urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.customers,PROD)`) -- The customers table contains the cust_email column with direct personal data exposure.
- **Order Details** (`urn:li:dataset:(urn:li:dataPlatform:looker,b2fd91.order-entry.explore.order_details,PROD)`) -- The Order Details table is a row-level operational table containing individual customer records with the source column cust_email along with numerous other PII fields, directly exposing the individual's personal data at order line item granularity.

## Needs human review
- **order_details** (`urn:li:dataset:(urn:li:dataPlatform:looker,b2fd91.order-entry-looker.view.order_details,PROD)`) -- The order_details asset's structure and contents are unknown, making it impossible to determine if individual records remain identifiable.
- **ORDER_DETAILS** (`urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.order_details,PROD)`) -- ORDER_DETAILS table structure is unknown and requires manual inspection to determine if it contains identifiable customer data.
- **ORDER_DETAILS** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.ORDER_DETAILS,PROD)`) -- ORDER_DETAILS is a transactional table and without knowing its schema or linkage to cust_email, human review is required.
- **Customer Analytics Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Customer_Analytics_Measures,PROD)`) -- The asset type and description are unknown, making it impossible to determine if personal data is still exposed or aggregated.
- **Essential KPI Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Essential_KPI_Measures,PROD)`) -- The asset type and description are insufficient to determine if the KPI measures are aggregated or contain row-level personal data.
- **Product Perfromance Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Product_Perfromance_Measures,PROD)`) -- The asset name suggests aggregation, but metadata is insufficient to confirm the absence of raw exposure.
- **Time Inteligence Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Time_Inteligence_Measures,PROD)`) -- The asset type 'Time Intelligence Measures' is ambiguous and lacks sufficient description to determine if it contains row-level data or aggregated metrics.
- **ORDER_DETAILS_REPLICA** (`urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.order_details_replica,PROD)`) -- ORDER_DETAILS_REPLICA's structure and content are unknown, making it impossible to determine whether it contains individual-level records with cust_email or only aggregated data without personal identifiers.

## No action
- **Geographic Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Geographic_Measures,PROD)`) -- Geographic Measures typically contains aggregated metrics at geographic levels, which do not directly expose individual customer email addresses or identifiable personal data.
