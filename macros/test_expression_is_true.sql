{% test expression_is_true(model, expression) %}


with validation as (
    select
        *
    from {{ model }}
),

validation_errors as (
    select
        *
    from validation
    where not ({{ expression }})
)

select * from validation_errors {% endtest %}