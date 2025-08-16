# dags/weather_etl_dag.py
from __future__ import annotations
import re
import unicodedata
from datetime import timedelta
import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from supporting_scripts.extract import get_weather_data
from supporting_scripts.transform import transform_weather_data
from supporting_scripts.load import load_data_to_postgres

VN_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    "owner": "you",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}

CITIES = ["Hanoi", "London", "Tokyo", "Sydney", "New York", "Da Lat"]
DATA_LAKE_PATH = "/opt/airflow/raw_data"

def slugify(s: str) -> str:
    s_norm = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s_norm = s_norm.lower().replace(" ", "_")
    s_norm = re.sub(r"[^a-z0-9_.-]", "_", s_norm)
    return s_norm

with DAG(
    dag_id="weather_data_etl_v2",
    description="ETL thời tiết: OpenWeather -> Postgres (5 phút/lần, giờ VN)",
    schedule_interval="*/5 * * * *",  # chạy 5 phút/lần
    start_date=pendulum.datetime(2025, 8, 13, 0, 0, tz=VN_TZ),  # đặt timezone ở đây
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["data-engineering", "project", "weather"],
) as dag:

    create_table = PostgresOperator(
        task_id="create_weather_table",
        postgres_conn_id="postgres_de_weather",
        sql="""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city VARCHAR(50) NOT NULL,
            temperature FLOAT,
            feels_like FLOAT,
            humidity INTEGER,
            wind_speed FLOAT,
            description VARCHAR(100),
            data_collection_utc TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (city, data_collection_utc)
        );
        """,
    )

    for city in CITIES:
        cid = slugify(city)
        extract_id = f"extract_{cid}"
        transform_id = f"transform_{cid}"
        load_id = f"load_{cid}"

        extract_task = PythonOperator(
            task_id=extract_id,
            python_callable=get_weather_data,
            op_kwargs={
                "api_key": "{{ var.value.OPENWEATHER_API_KEY }}",
                "city_name": city,
                "data_lake_path": DATA_LAKE_PATH,
            },
            pool="weather_api",
        )

        transform_task = PythonOperator(
            task_id=transform_id,
            python_callable=transform_weather_data,
            op_kwargs={
                "raw_data_path": "{{ ti.xcom_pull(task_ids='" + extract_id + "') }}",
            },
        )

        load_task = PythonOperator(
            task_id=load_id,
            python_callable=load_data_to_postgres,
            op_kwargs={
                "csv_path": "{{ ti.xcom_pull(task_ids='" + transform_id + "') }}",
                "pg_conn_id": "postgres_de_weather",
            },
        )

        create_table >> extract_task >> transform_task >> load_task
