# DSR Checklist -- subject `subj_demo_01`

Source column: `cust_email`
Downstream assets evaluated: 12

- 3 action needed
- 1 no action (aggregated, not personally identifiable)
- 8 needs human review

## Action needed
- **order_details** (`urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_details,PROD)`) -- The order_details table contains customer email addresses and other PII at a row-level grain (one row per order line item), directly exposing the individual's personal data without aggregation.
- **customers** (`urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.customers,PROD)`) -- The customers table contains customer demographic and contact information including the personal data column cust_email, which directly exposes the individual's identity and contact details.
- **Order Details** (`urn:li:dataset:(urn:li:dataPlatform:looker,b2fd91.order-entry.explore.order_details,PROD)`) -- The Order Details table is a row-level operational table containing individual customer records with the source column cust_email along with numerous other PII fields, directly exposing the individual's personal data at order line item granularity.

## Needs human review
- **ORDER_DETAILS** (`urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.order_details,PROD)`) -- ORDER_DETAILS table structure is unknown; it may contain customer identifiers linking to cust_email or be aggregated order summaries, requiring manual inspection to determine if the individual remains identifiable.
- **order_details** (`urn:li:dataset:(urn:li:dataPlatform:looker,b2fd91.order-entry-looker.view.order_details,PROD)`) -- The order_details asset's structure and contents are unknown, making it impossible to determine whether individual customer records remain identifiable through the cust_email column or derived associations.
- **ORDER_DETAILS** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.ORDER_DETAILS,PROD)`) -- ORDER_DETAILS is typically a transactional table that likely contains order-level records, but without knowing its specific schema and whether it contains or can be linked back to cust_email, human review is needed to determine if individual records are still identifiable.
- **Customer Analytics Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Customer_Analytics_Measures,PROD)`) -- The asset type is unknown and no description is provided, making it impossible to determine whether customer email data is still directly exposed or only aggregated/derived metrics are present.
- **Essential KPI Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Essential_KPI_Measures,PROD)`) -- The asset type is unknown and no description is provided, making it impossible to determine whether the KPI measures contain row-level personal data or are aggregated metrics.
- **Product Perfromance Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Product_Perfromance_Measures,PROD)`) -- The asset name "Product Performance Measures" suggests aggregated data, but without details on its structure, granularity, and whether it filters or indexes by customer email, human review is needed to confirm the individual is not identifiable.
- **Time Inteligence Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Time_Inteligence_Measures,PROD)`) -- The asset type 'Time Intelligence Measures' is ambiguous and no description was provided, making it unclear whether it contains row-level customer data or only aggregated metrics derived from the cust_email column.
- **ORDER_DETAILS_REPLICA** (`urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.analytics.order_details_replica,PROD)`) -- ORDER_DETAILS_REPLICA's structure and content are unknown, making it impossible to determine whether it contains individual-level records with cust_email or only aggregated data without personal identifiers.

## No action
- **Geographic Measures** (`urn:li:dataset:(urn:li:dataPlatform:powerbi,b2fd91.datahub_order_entries.Geographic_Measures,PROD)`) -- Geographic Measures typically contains aggregated metrics at geographic levels (e.g., regional, state, country), which do not directly expose individual customer email addresses or identifiable personal data.
