"""
database.py — Gestionnaire JSON pour Neurostep
"""

import json
from pathlib import Path
import os

DB_PATH = Path(__file__).parent / "data" / "database.json"

def get_data() -> dict:
    if not DB_PATH.exists():
        return {"applications": [], "troubles": [], "themes": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: dict):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_all_apps() -> list[dict]:
    return get_data().get("applications", [])

def get_app_by_id(app_id: int) -> dict | None:
    apps = get_all_apps()
    for app in apps:
        if app.get("id") == app_id:
            return app
    return None

def insert_app(app_data: dict) -> int:
    data = get_data()
    apps = data.get("applications", [])
    new_id = max([a.get("id", 0) for a in apps] + [0]) + 1
    app_data["id"] = new_id
    apps.append(app_data)
    data["applications"] = apps
    save_data(data)
    return new_id

def update_app(app_id: int, updated_data: dict):
    data = get_data()
    apps = data.get("applications", [])
    for idx, app in enumerate(apps):
        if app.get("id") == app_id:
            apps[idx].update(updated_data)
            break
    data["applications"] = apps
    save_data(data)

def get_all_troubles() -> list[str]:
    return get_data().get("troubles", [])

def add_trouble(trouble: str):
    data = get_data()
    troubles = data.get("troubles", [])
    if trouble not in troubles:
        troubles.append(trouble)
        data["troubles"] = troubles
        save_data(data)

def get_all_themes() -> list[str]:
    return get_data().get("themes", [])

