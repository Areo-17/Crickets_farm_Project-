--CREATE SCHEMAS
create schema silver;
create schema gold;

create table silver.aggregated_data 
(
    fecha_registro date
    fecha_nacimiento date,
    tipo text
    volumen int,
    fecha_reproduccion_esperada date,
    fecha_reproduccion_esperada date
);

WITH agreggated_data AS (
    select 
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
from "farm-data"
),
pre as (
    select 
        count(*) as number_of_boxes,
        EXTRACT(MONTH FROM fecha_sacrificio_esperada) as month,
        tipo as type
    from agreggated_data
    group by 2,3
),
PROD AS (
    SELECT 
        month,
        type,
        number_of_boxes,
        CASE 
            WHEN type = 'E' THEN number_of_boxes * 2.5
            WHEN type = 'R' THEN number_of_boxes * 1.5
        END as flour_produced_kg
    FROM PRE
)
SELECT
    TO_CHAR(TO_DATE(month::text, 'MM'), 'Month') as mes, 
    sum(number_of_boxes) as numero_de_cajas,
    sum(flour_produced_kg) as total_kg_harina
FROM PROD
GROUP BY 1;



-------------------------
-- Active: 1723177139166@@127.0.0.1@5432@grillos@public
select column_name, data_type
from information_schema.columns
where table_name = 'farm-data';


select * from "farm-data"


select tipo from "farm-data"
group by tipo

select 
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
from "farm-data"

alter table "farm-data" add column id serial primary key;
alter table "farm-data" add column created_at timestamp default now();



create schema silver;
create schema gold;


