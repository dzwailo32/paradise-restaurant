import hashlib
import hmac
import sqlite3
from flask import Flask, request, redirect

app = Flask(__name__)

DB_NAME = "restaurant.db"
SECRET_KEY = "Paradise_QR_Secret_2026_DZ"
NUM_TABLES = 32

MENU_ITEMS = [
    ("Menu Pizza", "Pizza Margherita", 0),
    ("Menu Pizza", "Pizza Burata", 0),
    ("Menu Pizza", "Pizza Grand Bleu", 0),
    ("Menu Pizza", "Pizza Fruits de Mer", 0),
    ("Menu Pizza", "Pizza Paradise", 0),
    ("Entrées Froides", "Salade César", 0),
    ("Entrées Chaudes", "Poulpe à la Galicienne", 0),
    ("Viandes Rouge", "Côte de Veau", 0),
    ("Viandes Rouge", "Grillades Paradise (BBQ)", 0),
    ("Viandes Blanche", "Brochette de Poulet (BBQ)", 0),
    ("Menu Poissons", "Saumon Frais", 0),
    ("Menu Poissons", "Paella Royale sur Commande (Min 2 Personnes)", 0),
    ("Menu Enfant", "Cheese Burger (V-H 100g)", 0),
    ("Menu Enfant", "Nuggets", 0),
    ("Spécialités & Suppléments", "Supplément Sauce Viande (Poivre/Roquefort/Champignons)", 0),
    ("Spécialités & Suppléments", "Supplément Sauce Poisson (Citronné/à l'Orange/Dugléré)", 0),
]

SHARED_STYLE = """
<style>
  body {
    background-color: #faf7f2;
    color: #1f2421;
    font-family: system-ui, -apple-system, "Segoe UI", Tahoma, Arial, sans-serif;
    margin: 0;
    padding: 16px;
    line-height: 1.5;
  }
  .container {
    max-width: 900px;
    margin: 0 auto;
  }
  h1, h2, .menu-header {
    background: linear-gradient(135deg, #17201b, #28382f);
    color: #fff8e7;
    padding: 12px 16px;
    border-radius: 12px;
    border-bottom: 3px solid #c59b27;
    margin-top: 0;
  }
  legend {
    background-color: #1e2923;
    color: #fffdf7;
    padding: 8px 14px;
    border-radius: 10px;
    border-right: 4px solid #c59b27;
    width: auto;
    font-weight: bold;
  }
  fieldset, .card, .menu-item, ul li {
    list-style: none;
    background-color: #ffffff;
    border: 1px solid #e6dfd3;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  }
  .item-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #f1ece2;
  }
  .item-row:last-child {
    border-bottom: none;
  }
  input[type="number"] {
    width: 72px;
    padding: 6px 8px;
    border: 1px solid #cfc5b4;
    border-radius: 8px;
    font-size: 15px;
  }
  button[type="submit"], button, .btn {
    background-color: #1e2923;
    color: #fff8e7;
    border: 2px solid #c59b27;
    border-radius: 10px;
    padding: 11px 22px;
    font-size: 16px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
  }
  button[type="submit"]:hover, button:hover, .btn:hover {
    background-color: #2b3a32;
  }
</style>
"""


def make_token(table_num: int) -> str:
    msg = f"table:{table_num}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:16]


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num INTEGER NOT NULL,
            items_summary TEXT NOT NULL,
            total INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending'
        )
        """
    )
    count = c.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count == 0:
        c.executemany(
            "INSERT INTO menu_items (category, name, price) VALUES (?, ?, ?)",
            MENU_ITEMS,
        )
    conn.commit()
    conn.close()


def verify_table_request(table_raw: str, token: str):
    try:
        table_num = int(table_raw)
    except (ValueError, TypeError):
        return None
    if table_num < 1 or table_num > NUM_TABLES:
        return None
    full_expected = make_token(table_num)
    valid_tokens = {full_expected, full_expected[:12]}
    if not token or not any(hmac.compare_digest(token, t) for t in valid_tokens):
        return None
    return table_num


@app.route("/", methods=["GET", "POST"])
def menu():
    init_db()
    if request.method == "POST":
        table_raw = request.form.get("table_num", "").strip()
        token = request.form.get("token", "").strip()
    else:
        table_raw = request.args.get("table", "").strip()
        token = request.args.get("token", "").strip()

    table_num = verify_table_request(table_raw, token)
    if not table_num:
        return (
            f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='utf-8'>"
            f"<title>Paradise - تنبيه</title>{SHARED_STYLE}</head><body>"
            f"<div class='container'><div class='card'><h2>رقم الطاولة غير صالح.</h2>"
            f"<p>يرجى مسح رمز QR الخاص بالطاولة للدخول بشكل صحيح.</p></div></div></body></html>",
            403,
        )

    conn = sqlite3.connect(DB_NAME)
    menu_items = conn.execute(
        "SELECT id, category, name, price FROM menu_items ORDER BY id"
    ).fetchall()

    if request.method == "POST":
        chosen = []
        total = 0
        for iid, cat, name, price in menu_items:
            qty_raw = request.form.get(f"qty_{iid}", "0").strip()
            try:
                qty = max(0, int(qty_raw))
            except ValueError:
                qty = 0
            if qty > 0:
                chosen.append(f"{name} (x{qty})")
                total += price * qty

        if chosen:
            summary = " | ".join(chosen)
            conn.execute(
                "INSERT INTO orders (table_num, items_summary, total, status) VALUES (?, ?, ?, 'pending')",
                (table_num, summary, total),
            )
            conn.commit()
            conn.close()
            return (
                f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='utf-8'>"
                f"<title>تم إرسال الطلب - Paradise</title>{SHARED_STYLE}</head><body>"
                f"<div class='container'><div class='card'><h2>تم إرسال طلب الطاولة رقم {table_num}</h2>"
                f"<p>{summary}</p>"
                f"<a class='btn' href='/?table={table_num}&token={token}'>العودة إلى القائمة</a>"
                f"</div></div></body></html>"
            )

    conn.close()

    grouped = {}
    for iid, cat, name, price in menu_items:
        grouped.setdefault(cat, []).append((iid, name, price))

    sections_html = []
    for cat, items in grouped.items():
        rows = []
        for iid, name, price in items:
            price_label = f"{price} DA" if price > 0 else "حسب القائمة"
            rows.append(
                f"<div class='item-row'>"
                f"<div><b>{name}</b><div style='color:#6b655b;font-size:13px;'>{price_label}</div></div>"
                f"<input type='number' name='qty_{iid}' min='0' value='0'>"
                f"</div>"
            )
        sections_html.append(f"<fieldset><legend>{cat}</legend>{''.join(rows)}</fieldset>")

    return (
        f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>Paradise - قائمة الطعام</title>{SHARED_STYLE}</head><body>"
        f"<div class='container'>"
        f"<h2>Paradise - قائمة الطعام | طاولة رقم {table_num}</h2>"
        f"<form method='post'>"
        f"<input type='hidden' name='table_num' value='{table_num}'>"
        f"<input type='hidden' name='token' value='{token}'>"
        f"{''.join(sections_html)}"
        f"<button type='submit'>إرسال الطلب</button>"
        f"</form></div></body></html>"
    )


@app.route("/kitchen")
def kitchen():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    orders = conn.execute(
        "SELECT id, table_num, items_summary, total, status FROM orders ORDER BY id DESC"
    ).fetchall()
    conn.close()

    cards = []
    for oid, tnum, summary, total, status in orders:
        status_ar = "قيد التحضير" if status == "pending" else "جاهز"
        action_btn = (
            f"<a class='btn' href='/kitchen/done/{oid}'>تم التحضير</a>"
            if status == "pending"
            else f"<span style='color:#2e7d32;font-weight:bold;'>✓ مكتمل</span>"
        )
        cards.append(
            f"<div class='card'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
            f"<b>طلب #{oid} — طاولة {tnum}</b><span>{status_ar}</span></div>"
            f"<p style='margin:8px 0;'>{summary}</p>"
            f"{action_btn}</div>"
        )

    body_content = "".join(cards) if cards else "<div class='card'>لا توجد طلبات حالياً.</div>"

    return (
        f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='5'>"
        f"<title>Paradise - المطبخ</title>{SHARED_STYLE}</head><body>"
        f"<div class='container'><h2>Paradise - شاشة المطبخ</h2>{body_content}</div>"
        f"</body></html>"
    )


@app.route("/kitchen/done/<int:oid>")
def kitchen_done(oid: int):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE orders SET status='done' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    return redirect("/kitchen")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
