{% test textual(model, column_name) %}

-- Test that a column is of a text/string/varchar type
-- This test checks the data type of the column in the database


select
    column_name,
    data_type
from information_schema.columns
where table_schema = '{{ model.schema }}'
  and table_name = '{{ model.name }}'
  and column_name = '{{ column_name }}'
  and data_type not in ('character varying', 'varchar', 'text', 'character', 'char', 'string')

{% endtest %}