{% macro log_job_run(job_name, status, error_message=none, run_duration=none) %}
    {#
    Macro to log job execution details to the ctl.job_run_log table
    
    Args:
        job_name: Name of the job/model being executed
        status: 'success', 'failure', or 'running'
        error_message: Error details if status is 'failure'
        run_duration: Duration in seconds (optional)
    
    Usage:
        {{ log_job_run('stg_customer', 'success') }}
        {{ log_job_run('stg_orders', 'failure', 'Connection timeout') }}
    #}
    
    {% set query %}
        insert into {{ target.schema }}.ctl.job_run_log (
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
            '{{ invocation_id }}_{{ job_name }}_{{ modules.datetime.datetime.now().strftime("%Y%m%d%H%M%S") }}',
            '{{ run_started_at }}',
            current_timestamp,
            '{{ job_name }}',
            'dbt_model',
            '{{ status }}',
            {% if error_message %}
                '{{ error_message }}'
            {% else %}
                null
            {% endif %},
            {% if run_duration %}
                {{ run_duration }}
            {% else %}
                null
            {% endif %},
            '{{ invocation_id }}',
            '{{ target.name }}'
        )
    {% endset %}
    
    {% do run_query(query) %}
    
{% endmacro %}