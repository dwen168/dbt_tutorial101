https://github.com/dbt-labs/jaffle-shop/blob/main/README.md

Load the data
There are a few ways to load the data for the project:

Using the sample data in the repo. Seeds are static data files in CSV format that dbt will upload, usually for reference models, like US zip codes mapped to country regions for example, but in this case the feature is hacked to do some data ingestion. This is not what seeds are meant to be used for (dbt is not a data loading tool), but it's useful for this project to give you some data to get going with quickly. Run the command below and when it's done either delete the seeds/jaffle-data folder, remove jaffle-data config from the dbt_project.yml, or ideally, both.
dbt seed --full-refresh --vars '{"load_source_data": true}'
