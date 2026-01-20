
{% macro log_run_results(results) %}
    {% if execute %}
        {% for res in results %}
            {% set node = res.node %}
            {% set job_name = node.name %}
            {% set status = res.status %}
            
            {% set raw_msg = res.message | replace("'", "''") if res.message else '' %}
            {% set is_err = status in ('error', 'fail', 'warn') %}
            
            {% set rows_affected = res.adapter_response.get('rows_affected') if res.adapter_response else none %}
            
            {% set materialization = node.config.get('materialized') %}
            {% set relation = node.relation_name | replace('"', '') if node.relation_name else job_name %}
            
            {% set target_rows = none %}
            {% if not is_err and status == 'success' and node.resource_type in ('model', 'seed') %}
                {% set count_query %}
                    select count(*) from {{ node.relation_name }}
                {% endset %}
                {% set results_count = run_query(count_query) %}
                {% if results_count %}
                    {% set target_rows = results_count.columns[0].values()[0] %}
                {% endif %}
            {% endif %}

            {% set query %}
                insert into ctl.job_run_log (
                    job_run_id,
                    run_started_at,
                    run_completed_at,
                    job_name,
                    job_type,
                    status,
                    error_message,
                    adapter_response,
                    rows_affected,
                    target_rows,
                    run_duration_seconds,
                    invocation_id,
                    target_name,
                    destination_table,
                    materialization_type,
                    is_full_refresh,
                    source_file_path
                )
                values (
                    '{{ invocation_id }}_{{ job_name }}_{{ loop.index }}',
                    '{{ run_started_at }}',
                    current_timestamp,
                    '{{ job_name }}',
                    '{{ node.resource_type }}',
                    '{{ status }}',
                    {% if is_err %} '{{ raw_msg }}' {% else %} null {% endif %},
                    {% if not is_err %} '{{ raw_msg }}' {% else %} null {% endif %},
                    {% if rows_affected is not none %} {{ rows_affected }} {% else %} null {% endif %},
                    {% if target_rows is not none %} {{ target_rows }} {% else %} null {% endif %},
                    {{ res.execution_time }},
                    '{{ invocation_id }}',
                    '{{ target.name }}',
                    '{{ relation }}',
                    '{{ materialization if materialization else node.resource_type }}',
                    {{ flags.FULL_REFRESH }},
                    '{{ node.original_file_path }}'
                )
            {% endset %}
            
            {% do run_query(query) %}
        {% endfor %}
    {% endif %}
{% endmacro %}