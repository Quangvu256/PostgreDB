import pandas as pd
from typing import Optional, Sequence, Tuple

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2 import sql
from psycopg2.extras import execute_values

TABLE_NAME = "weather_data"
COLUMNS: Sequence[str] = (
    "city",
    "temperature",
    "feels_like",
    "humidity",
    "wind_speed",
    "description",
    "data_collection_utc",
)

def _to_tuples(df: pd.DataFrame) -> Sequence[Tuple]:
    df2 = df.reindex(columns=COLUMNS)
    return [tuple(row) for row in df2.itertuples(index=False, name=None)]

def load_data_to_postgres(csv_path: str, pg_conn_id: str = "postgres_de_weather") -> Optional[int]:
    """
    Đọc CSV và bulk insert vào PostgreSQL qua PostgresHook.
    ON CONFLICT (city, data_collection_utc) DO NOTHING để idempotent.
    """
    if not csv_path:
        raise ValueError("[load] Empty csv_path")

    df = pd.read_csv(csv_path)
    values = _to_tuples(df)

    hook = PostgresHook(postgres_conn_id=pg_conn_id)
    conn = hook.get_conn()
    conn.autocommit = False

    insert_query = sql.SQL("""
        INSERT INTO {table} ({cols}) VALUES %s
        ON CONFLICT (city, data_collection_utc) DO NOTHING
    """).format(
        table=sql.Identifier(TABLE_NAME),
        cols=sql.SQL(", ").join(map(sql.Identifier, COLUMNS)),
    )

    try:
        with conn, conn.cursor() as cur:
            if values:
                execute_values(cur, insert_query, values, page_size=1000)
        print(f"[load] Attempted insert rows: {len(values)} into {TABLE_NAME}")
        return len(values)
    except Exception as e:
        print(f"[load] Insert error: {e}")
        raise
    finally:
        conn.close()
