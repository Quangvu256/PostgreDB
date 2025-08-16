import json
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path

def transform_weather_data(raw_data_path: str) -> str:
    """
    Đọc JSON thô -> chuẩn hóa -> lưu CSV và trả về đường dẫn CSV (string).
    """
    if not raw_data_path:
        raise ValueError("[transform] Empty raw_data_path")

    p = Path(raw_data_path)
    if not p.exists():
        raise FileNotFoundError(f"[transform] Not found: {raw_data_path}")

    with open(p, "r", encoding="utf-8") as f:
        raw = json.load(f)

    city = raw.get("name")
    main = raw.get("main", {}) or {}
    wind = raw.get("wind", {}) or {}
    weather_list = raw.get("weather", []) or [{}]
    desc = (weather_list[0] or {}).get("description")

    dt_unix = raw.get("dt")
    if dt_unix is None:
        raise ValueError("[transform] Missing 'dt' in raw JSON")

    dt_utc = datetime.fromtimestamp(dt_unix, tz=timezone.utc).replace(tzinfo=None)

    if not city or main.get("temp") is None:
        raise ValueError("[transform] Invalid data: missing city or temperature")

    row = {
        "city": city,
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "description": desc,
        "data_collection_utc": dt_utc,
    }

    df = pd.DataFrame([row])
    out_path = p.with_suffix(".csv")
    df.to_csv(out_path, index=False)
    print(f"[transform] Saved CSV: {out_path}")
    return str(out_path)
