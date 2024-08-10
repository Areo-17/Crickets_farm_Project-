from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 9),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag = DAG(
    'grillos_operations',
    default_args=default_args,
    description='DAG with SQL operations on PostgreSQL for a grillos farm.',
    schedule_interval='*/5 * * * *',
)

create_schemas = PostgresOperator(
    task_id='create_schemas',
    postgres_conn_id='postgres_conn',
    sql="""
    BEGIN;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
    COMMIT;
    """,
    dag=dag,
)

create_silver_gold = PostgresOperator(
    task_id='create_silver_gold',
    postgres_conn_id='postgres_conn',
    sql="""
    DROP TABLE IF EXISTS silver.aggregated_data;
    CREATE TABLE silver.aggregated_data (
        fecha_registro DATE,
        fecha_nacimiento DATE,
        tipo TEXT,
        volumen INT,
        fecha_reproduccion_esperada DATE,
        fecha_sacrificio_esperada DATE
    );

    -- Ingestar datos desde farm-data hacia silver
    INSERT INTO silver.aggregated_data
    SELECT 
        fecha_registro::date,
        fecha_nacimiento::date,
        tipo,
        volumen,
        CASE 
            WHEN tipo = 'R' THEN fecha_nacimiento::date + interval '42 days'
            WHEN tipo = 'S' THEN fecha_nacimiento::date + interval '45 days'
        END as fecha_reproduccion_esperada,
        CASE 
            WHEN tipo = 'R' THEN fecha_nacimiento::date + interval '54 days'
            WHEN tipo = 'S' THEN fecha_nacimiento::date + interval '35 days'
        END as fecha_sacrificio_esperada
    FROM "farm-data";

    -- Crear y poblar la tabla gold
    DROP TABLE IF EXISTS gold.monthly_production;
    CREATE TABLE gold.monthly_production AS
    WITH pre AS (
        SELECT 
            count(*) as number_of_boxes,
            EXTRACT(MONTH FROM fecha_sacrificio_esperada) as month,
            tipo as type
        FROM silver.aggregated_data
        GROUP BY 2, 3
    ),
    prod AS (
        SELECT 
            month,
            type,
            number_of_boxes,
            CASE 
                WHEN type = 'E' THEN number_of_boxes * 2.5
                WHEN type = 'R' THEN number_of_boxes * 1.5
            END as flour_produced_kg
        FROM pre
    )
    SELECT
        TO_CHAR(TO_DATE(month::text, 'MM'), 'Month') as mes, 
        sum(number_of_boxes) as numero_de_cajas,
        sum(flour_produced_kg) as total_kg_harina
    FROM prod
    GROUP BY 1;
    """,
    dag=dag,
)

create_schemas >> create_silver_gold