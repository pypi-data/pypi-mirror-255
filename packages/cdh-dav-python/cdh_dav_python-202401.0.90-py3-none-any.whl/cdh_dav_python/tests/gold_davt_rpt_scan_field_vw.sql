/**
 * View Name: TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET.gold_davt_rpt_scan_field_vw
 * 
 * Description:
 * This view provides a consolidated metadata perspective of datasets within the bronze_clc_schema from the wonder_metadata_etl database,
 * including details such as dataset name, column name, description, data type, maximum length, row count, and percentage of empty values.
 * It is tailored to assist with data governance by offering an at-a-glance overview of data structure and integrity.
 * 
 * Columns:
 * - `table`: Represents the dataset name.
 * - field: The name of the field or column within the dataset.
 * - description: A comment describing the content or purpose of the field.
 * - type: The data type of the field.
 * - max_length: The maximum length/size of the field data type.
 * - n_rows: The total number of rows present in the dataset.
 * - n_row_checked: The number of rows checked for data quality (To be made configurable).
 * - percent_empty: The percentage of null values in the dataset field, indicating data completeness.
 * 
 * Joins:
 * This view does not perform any joins but may be joined with other metadata views or tables to enrich data context.
 * 
 * Filters:
 * Not applicable as this view presents metadata without applying any specific data filters.
 * 
 * Order:
 * The output is ordered by the dataset name to provide a structured overview.
 * 
 * Dependencies:
 * - wonder_metadata_etl.bronze_clc_schema: The source schema containing the dataset and field information.
 * 
 * Permissions:
 * Permissions should be set according to the database and application-level security protocols post-creation.
 * 
 * Notes:
 * - The placeholder TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET should be replaced with the specific target database name and visualization application code, respectively.
 * - Please ensure proper error handling for null values and division by zero cases in the percentage calculation.
 * 
 * Usage:
 * This view can be utilized by data governance tools and processes for monitoring and managing dataset health, compliance, and usage.
 * 
 * Created by: [Your Name or Identifier]
 * Creation date: [The date of view creation]
 */

Create
or replace view TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET.gold_davt_rpt_scan_field_vw as

Select
  dataset_name as table,
  column_name as field, 
  comment as description, 
  data_type_name as type, 
  max_length as max_length,
  row_count as n_rows,
  0 as n_row_checked /* TODO - make number rows to check configureable */,
  CASE
    WHEN row_count = 0 OR row_count IS NULL THEN NULL -- Handle divide by zero/null row_count
    ELSE null_count / NULLIF(row_count, 0) -- Safe division to calculate percentage
  END AS fraction_empty,
  unique_count as n_unique,
  CASE
    WHEN row_count = 0 OR row_count IS NULL THEN NULL -- Handle divide by zero/null row_count
    ELSE unique_count / NULLIF(row_count, 0) -- Safe division to calculate percentage
  END AS fraction_unique
from
  TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET.bronze_clc_schema
order by dataset_name;


GRANT ALL PRIVILEGES ON VIEW TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET.gold_davt_rpt_scan_field_vw TO `TEMPORARY_OPEN_BRACKETspecific_user_or_roleTEMPORARY_CLOSE_BRACKET`;
GRANT ALL PRIVILEGES ON VIEW TEMPORARY_OPEN_BRACKETtarget_databaseTEMPORARY_CLOSE_BRACKET.gold_davt_rpt_scan_field_vw TO `TEMPORARY_OPEN_BRACKETadmin_user_or_roleTEMPORARY_CLOSE_BRACKET`;