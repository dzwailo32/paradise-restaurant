# -*- coding: utf-8 -*-
import json
import os
import sqlite3
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "restaurant.db")
RENDER_API_URL = "https://paradise-restaurant-ato3.onrender.com/api/orders"
POLL_INTERVAL_SEC = 3


def init_sync_table(conn):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS synced_remote_orders (
            remote_id INTEGER PRIMARY KEY,
            local_order_id INTEGER
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.commit()


def get_max_remote_id(conn):
    row = conn.execute("SELECT COALESCE(MAX(remote_id), 0) FROM synced_remote_orders").fetchone()
    return int(row[0] or 0)


def fetch_remote_orders(since_id):
    url = f"{RENDER_API_URL}?since_id={since_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "ParadiseCashierSync/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("orders", [])


def sync_once():
    conn = sqlite3.connect(DB_PATH)
    init_sync_table(conn)
    since_id = get_max_remote_id(conn)
    remote_orders = fetch_remote_orders(since_id)

    added = 0
    for ro in remote_orders:
        rid = int(ro["remote_id"])
        exists = conn.execute(
            "SELECT 1 FROM synced_remote_orders WHERE remote_id = ?", (rid,)
        ).fetchone()
        if exists:
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


def main():
    print(f"[PARADISE SYNC] Connected to DB: {DB_PATH}")
    print(f"[PARADISE SYNC] Polling: {RENDER_API_URL}")
    while True:
        try:
            added = sync_once()
            if added > 0:
                print(f"[PARADISE SYNC] +{added} nouvelle(s) commande(s) ajoutée(s) à restaurant.db")
        except urllib.error.URLError as e:
            print(f"[PARADISE SYNC] Réseau / Render en attente: {e}")
        except Exception as e:
            print(f"[PARADISE SYNC] Erreur: {e}")
        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
