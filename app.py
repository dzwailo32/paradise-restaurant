import os
import hmac
import hashlib
import sqlite3
from flask import Flask, request, redirect

app = Flask(__name__)
DB_NAME = 'restaurant.db'

# يجب أن يطابق نفس SECRET_KEY الموجود في سكريبت توليد رموز QR
SECRET_KEY = os.environ.get("SECRET_KEY", "PARADISE_SECRET_KEY_CHANGE_ME_2026")


def make_table_token(table_no: int) -> str:
    msg = f"paradise-table-{table_no}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:12]


def verify_table_token(table_no: int, token: str) -> bool:
    if not token:
        return False
    expected = make_table_token(table_no)
    return hmac.compare_digest(expected, token.strip())


MENU_ITEMS = [
    ('Menu Pizza', 'Pizza Margherita', 0),
    ('Menu Pizza', 'Pizza Champignons', 0),
    ('Menu Pizza', 'Pizza Vegetarienne', 0),
    ('Menu Pizza', 'Pizza Campione', 0),
    ('Menu Pizza', 'Pizza Royale', 0),
    ('Menu Pizza', 'Pizza 4 Fromage', 0),
    ('Menu Pizza', 'Pizza Napolitana', 0),
    ('Menu Pizza', 'Pizza Crevettes', 0),
    ('Menu Pizza', 'Pizza Pecheur', 0),
    ('Menu Pizza', 'Pizza Fruits de Mer', 0),
    ('Menu Pizza', 'Pizza Paradise', 0),
    ('Menu Pizza', 'Pizza Burata', 0),
    ('Menu Pizza', 'Pizza Grand Bleu', 0),
    ('Entrées Froides', 'Salade César', 0),
    ('Entrées Froides', 'Salade Variée', 0),
    ('Entrées Froides', 'Camembert Farcie aux Fruits Secs', 0),
    ('Entrées Froides', 'Salade du Vieux Port', 0),
    ('Entrées Froides', 'Fraîcheur Paradise au Choix du Chef', 0),
    ('Entrées Froides', 'Carpaccio de Crevette', 0),
    ('Entrées Chaudes', 'Hrira', 0),
    ('Entrées Chaudes', 'Soupe de Poissons', 0),
    ('Entrées Chaudes', 'Bourek 2 pcs', 0),
    ('Entrées Chaudes', 'Bestilla au Poulet', 0),
    ('Entrées Chaudes', 'Briouttes au Crevettes', 0),
    ('Entrées Chaudes', 'Khlii (Khli3)', 0),
    ('Entrées Chaudes', 'Gratin de Poulet', 0),
    ('Entrées Chaudes', 'Gratin de Crevettes', 0),
    ('Entrées Chaudes', 'Camembert BBQ Roti aux Fruits Secs et Miel', 0),
    ('Entrées Chaudes', 'Crevettes Scampi Sauce Tartare', 0),
    ('Entrées Chaudes', 'Burger Paradise (V-H 200g)', 0),
    ('Entrées Chaudes', 'Poulpe à la Galicienne', 0),
    ('Menu Enfant', 'Cheese Burger (V-H 100g)', 0),
    ('Menu Enfant', 'Nuggets', 0),
    ('Viandes Blanche', 'Brochette de Poulet (BBQ)', 0),
    ('Viandes Blanche', "Poulet Biryani à l'Indienne Sauce Crémeuse", 0),
    ('Viandes Blanche', 'Cordon Bleu', 0),
    ('Viandes Blanche', 'Ballotine de Volaille aux Duxelles de Champignons', 0),
    ('Viandes Blanche', 'Supreme de Poulet Gratinés aux Fruits de Mer', 0),
    ('Viandes Rouge', 'Brochette Mixte (BBQ)', 0),
    ('Viandes Rouge', 'Steak Hachée (BBQ) Gratiné aux Duxelle de Champignons', 0),
    ('Viandes Rouge', "Cotelette d'Agneau (BBQ)", 0),
    ('Viandes Rouge', 'Roulade de Veau Sauce Chasseur', 0),
    ('Viandes Rouge', "Entrecôte de Veau (BBQ) Beurre Maître d'Hôtel", 0),
    ('Viandes Rouge', 'Filet de Veau (BBQ)', 0),
    ('Viandes Rouge', 'Tadjine Mhamer', 0),
    ('Viandes Rouge', 'Foie de Veau (Sauté - Grillé - en Sauce)', 0),
    ('Viandes Rouge', "Rôti d'Agneau Farci aux Fruits Sec", 0),
    ('Viandes Rouge', 'Grillades Paradise (BBQ)', 0),
    ('Viandes Rouge', 'Côte de Veau', 0),
    ('Spécialités & Suppléments', 'Supplément Sauce Viande (Poivre/Roquefort/Champignons)', 0),
    ('Spécialités & Suppléments', 'Spécialités Turques sur Commande', 0),
    ('Menu Poissons', "Crevettes Grillées ou Sautées à l'Ail", 0),
    ('Menu Poissons', 'Crevettes Décortiquées en Sauce', 0),
    ('Menu Poissons', 'Crevettes à la Sauce Dugléré', 0),
    ('Menu Poissons', "Calamars Frits ou Sautés à l'Ail", 0),
    ('Menu Poissons', 'Calamars Farcis', 0),
    ('Menu Poissons', 'Dorade Grillée (BBQ) ou au Four', 0),
    ('Menu Poissons', 'Mélange de Poissons', 0),
    ('Menu Poissons', 'Merlan Frit / au Four / Pané', 0),
    ('Menu Poissons', 'Lotte Caramélisée', 0),
    ('Menu Poissons', 'Pavé de Mérou', 0),
    ('Menu Poissons', 'Roulade de Poisson en Croûte', 0),
    ('Menu Poissons', 'Espadon Grillé (BBQ)', 0),
    ('Menu Poissons', 'Crevettes Royales', 0),
    ('Menu Poissons', 'Saumon Frais', 0),
    ('Menu Poissons', 'Mélange Royal', 0),
    ('Menu Poissons', "Supplément Sauce Poisson (Citronné/à l'Orange/Dugléré)", 0),
    ('Menu Poissons', 'Paella Royale sur Commande (Min 2 Personnes)', 0),
    ('Menu Poissons', 'Pièce de Poisson selon Disponibilité', 0),
]


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, name TEXT NOT NULL, price REAL NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, table_num TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT "pending")')
    c.execute('SELECT COUNT(*) FROM menu')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO menu (category, name, price) VALUES (?, ?, ?)', MENU_ITEMS)
    conn.commit()
    conn.close()


# تهيئة قاعدة البيانات عند التشغيل عبر Gunicorn أو مباشرة
init_db()


@app.route('/', methods=['GET', 'POST'])
def customer_menu():
    if request.method == 'POST':
        table_raw = request.form.get('table_num', '').strip()
        token = request.form.get('table_token', '').strip()
    else:
        table_raw = request.args.get('table', '').strip()
        token = request.args.get('token', '').strip()

    try:
        table_no = int(table_raw)
    except ValueError:
        return '<html dir="rtl"><head><meta charset="utf-8"></head><body><h3>رقم الطاولة غير صالح.</h3></body></html>', 400

    if not verify_table_token(table_no, token):
        return (
            '<html dir="rtl"><head><meta charset="utf-8"></head><body>'
            '<h3>رمز التحقق الخاص بالطاولة غير صالح أو تم تعديل رقم الطاولة.</h3>'
            '<p>يرجى مسح رمز QR الموجود على الطاولة الصحيحة.</p>'
            '</body></html>',
            403,
        )

    table_num = str(table_no)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        c.execute('SELECT id, name, price FROM menu')
        menu_items = c.fetchall()
        chosen, total = [], 0.0
        for item_id, name, price in menu_items:
            qty = int(request.form.get(f'qty_{item_id}', 0))
            if qty > 0:
                chosen.append(f'{name} (x{qty})')
                total += price * qty
        if chosen:
            c.execute(
                'INSERT INTO orders (table_num, items, total, status) VALUES (?, ?, ?, "pending")',
                (table_num, ' + '.join(chosen), total),
            )
            conn.commit()
            conn.close()
            safe_link = f"/?table={table_no}&token={token}"
            return (
                f'<html dir="rtl"><head><meta charset="utf-8"></head><body>'
                f'<h2>Paradise - تم إرسال الطلب (طاولة {table_num})</h2>'
                f'<p>المجموع: {total} دج</p>'
                f'<a href="{safe_link}">طلب جديد</a> | <a href="/kitchen">المطبخ</a>'
                f'</body></html>'
            )

    c.execute('SELECT id, category, name, price FROM menu ORDER BY id ASC')
    menu_items = c.fetchall()
    conn.close()

    grouped = {}
    for iid, cat, name, price in menu_items:
        grouped.setdefault(cat, []).append((iid, name, price))

    sections_html = ''
    for cat, items in grouped.items():
        rows = ''.join([
            f'<p style="margin:4px 0;"><b>{name}</b> ({price} دج) : '
            f'<input type="number" name="qty_{iid}" value="0" min="0" max="20" style="width:55px;"></p>'
            for iid, name, price in items
        ])
        sections_html += f'<fieldset style="margin:12px 0;padding:10px;"><legend><b>{cat}</b></legend>{rows}</fieldset>'

    return (
        f'<html dir="rtl"><head><meta charset="utf-8"><title>Paradise - Menu</title></head>'
        f'<body style="font-family:Arial,sans-serif;max-width:750px;margin:auto;padding:15px;">'
        f'<h1>Paradise - قائمة الطعام (طاولة {table_num})</h1>'
        f'<form method="POST">'
        f'<input type="hidden" name="table_num" value="{table_no}">'
        f'<input type="hidden" name="table_token" value="{token}">'
        f'{sections_html}'
        f'<button type="submit" style="padding:10px 20px;font-size:16px;">إرسال الطلب</button>'
        f'</form><hr><a href="/kitchen">شاشة المطبخ</a></body></html>'
    )


@app.route('/kitchen')
def kitchen():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, table_num, items FROM orders WHERE status="approved" ORDER BY id ASC')
    orders = c.fetchall()
    conn.close()
    blocks = ''.join([
        f'<div style="border:1px solid #999;padding:10px;margin:8px 0;">'
        f'<b>Paradise | طاولة {t} - طلب #{oid}</b><br>{items}<br>'
        f'<a href="/done/{oid}">تم التحضير</a></div>'
        for oid, t, items in orders
    ])
    return (
        f'<html dir="rtl"><head><meta charset="utf-8"><meta http-equiv="refresh" content="5">'
        f'<title>Paradise - المطبخ</title></head>'
        f'<body><h2>Paradise - شاشة المطبخ</h2>{blocks or "لا توجد طلبات حالياً"}</body></html>'
    )


@app.route('/done/<int:oid>')
def done(oid):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('UPDATE orders SET status="done" WHERE id=?', (oid,))
    conn.commit()
    conn.close()
    return redirect('/kitchen')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
