import requests
import json
from pathlib import Path

def get_weather_data(api_key: str, city_name: str, data_lake_path: str) -> str:
    """
    Gọi OpenWeather API, lưu JSON thô và trả về đường dẫn file (string).
    """
    url = (
        "http://api.openweathermap.org/data/2.5/weather"
        f"?q={city_name}&appid={api_key}&units=metric"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        ts = data.get("dt")
        file_path = Path(data_lake_path) / f"{city_name}_{ts}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[extract] Saved raw JSON: {file_path}")
        return str(file_path)
    except requests.exceptions.RequestException as e:
        print(f"[extract] HTTP error for city={city_name}: {e}")
        return ""
    except Exception as e:
        print(f"[extract] Unexpected error: {e}")
        return ""
