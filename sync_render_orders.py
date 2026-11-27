import json
import os
import sqlite3
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "restaurant.db")
API_URL = "https://paradise-restaurant-ato3.onrender.com/api/orders"


def init_db(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS synced_remote_orders (remote_id INTEGER PRIMARY KEY, local_order_id INTEGER)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, table_num TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT '')"
    )
    conn.commit()


def sync_once():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    since_id = int(
        conn.execute("SELECT COALESCE(MAX(remote_id), 0) FROM synced_remote_orders").fetchone()[0] or 0
    )
    req = urllib.request.Request(
        f"{API_URL}?since_id={since_id}",
        headers={"User-Agent": "ParadiseCashier/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        orders = json.loads(resp.read().decode("utf-8")).get("orders", [])

    added = 0
    for ro in orders:
        rid = int(ro["remote_id"])
        if conn.execute("SELECT 1 FROM synced_remote_orders WHERE remote_id = ?", (rid,)).fetchone():
            continue
        cur = conn.execute(
            "INSERT INTO orders (table_num, items, total, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                str(ro.get("table_num", "")),
                str(ro.get("items", "")),
                float(ro.get("total", 0.0)),
                str(ro.get("status", "pending")),
                str(ro.get("created_at", "")),
            ),
        )
        conn.execute(
            "INSERT INTO synced_remote_orders (remote_id, local_order_id) VALUES (?, ?)",
            (rid, cur.lastrowid),
        )
        added += 1

    conn.commit()
    conn.close()
    return added


if __name__ == "__main__":
    print("Running sync on:", DB_PATH)
    while True:
        try:
            count = sync_once()
            if count > 0:
                print(f"+{count} order(s) synced!")
        except Exception as err:
            print("Error:", err)
        time.sleep(3)
