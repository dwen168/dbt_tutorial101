{% macro log_run_results(results) %}
    {# 
    This macro loops through dbt run/test results and logs each one 
    to the ctl.job_run_log table. Use it in on-run-end hooks.
    #}
    {% if execute %}
        {% for res in results %}
            {% set job_name = res.node.name %}
            {% set status = res.status %}
            {% set duration = res.execution_time %}
            {# Escape single quotes in error messages #}
            {% set error_msg = res.message | replace("'", "''") if res.message else none %}
            
            {% set query %}
                insert into ctl.job_run_log (
                    job_run_id,
                    run_started_at,
                    run_completed_at,
                    job_name,
                    job_type,
                    status,
                    error_message,
                    run_duration_seconds,
                    invocation_id,
                    target_name
                )
                values (
                    '{{ invocation_id }}_{{ job_name }}_{{ loop.index }}',
                    '{{ run_started_at }}',
                    current_timestamp,
                    '{{ job_name }}',
                    '{{ res.node.resource_type }}',
                    '{{ status }}',
                    {% if error_msg %} '{{ error_msg }}' {% else %} null {% endif %},
                    {{ duration }},
                    '{{ invocation_id }}',
                    '{{ target.name }}'
                )
            {% endset %}
            
            {% do run_query(query) %}
        {% endfor %}
    {% endif %}
{% endmacro %}