{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
    This macro overrides dbt's default schema naming behavior.
    
    Default behavior: {target_schema}_{custom_schema}
    New behavior: 
    - If custom_schema is provided, use it directly (no prefix)
    - If no custom_schema, use target.schema from profiles.yml
    
    Examples:
    - profiles.yml schema: raw, +schema: staging -> Result: staging
    - profiles.yml schema: raw, no +schema -> Result: raw
    #}
    
    {%- set default_schema = target.schema -%}
    
    {%- if custom_schema_name is none -%}
        {# No custom schema specified, use the default from profile #}
        {{ default_schema }}
    {%- else -%}
        {# Custom schema specified, use it directly without prefix #}
        {{ custom_schema_name | trim }}
    {%- endif -%}

{%- endmacro %}