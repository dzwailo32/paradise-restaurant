import sqlite3
from flask import Flask, request, redirect

app = Flask(__name__)

DB_NAME = "restaurant.db"
NUM_TABLES = 32

MENU_ITEMS = [
    ("Menu Pizza", "PIZZA MARGHERITA", "Sauce tomate, mozzarella, origan", 0),
    ("Menu Pizza", "PIZZA CHAMPIGNONS", "Sauce tomate, champignons frais, fromage", 0),
    ("Menu Pizza", "PIZZA VEGETARIENNE", "Sauce tomate, légumes frais, origan, fromage", 0),
    ("Menu Pizza", "PIZZA CAMPIONE", "Sauce tomate, champignons frais, olives, fromage", 0),
    ("Menu Pizza", "PIZZA ROYALE", "Crème fraîche, poulet, champignons, fromage, pommes, fromage", 0),
    ("Menu Pizza", "PIZZA 4 FROMAGE", "Mélange de quatre fromages", 0),
    ("Menu Pizza", "PIZZA NAPOLITANA", "Sauce tomate, anchois, câpres, origan", 0),
    ("Menu Pizza", "PIZZA CREVETTES", "Sauce tomate, crevettes, fromage", 0),
    ("Menu Pizza", "PIZZA BURATA", "Sauce tomate, burrata fraîche, roquette", 0),
    ("Menu Pizza", "PIZZA GRAND BLEU", "Fruits de mer, ail, persil, fromage", 0),
    ("Menu Pizza", "PIZZA FRUITS DE MER", "Assortiment de fruits de mer et fromage", 0),
    ("Menu Pizza", "PIZZA PARADISE", "Spécialité maison Paradise", 0),
    ("Entrées Froides", "SALADE CÉSAR", "Laitue romaine, poulet grillé, croûtons, parmesan", 0),
    ("Entrées Chaudes", "POULPE À LA GALICIENNE", "Poulpe tendre, paprika, huile d'olive", 0),
    ("Viandes Rouge", "CÔTE DE VEAU", "Côte de veau grillée selon cuisson", 0),
    ("Viandes Rouge", "GRILLADES PARADISE (BBQ)", "Assortiment de grillades au feu de bois", 0),
    ("Viandes Blanche", "BROCHETTE DE POULET (BBQ)", "Brochette marinée grillée au BBQ", 0),
    ("Menu Poissons", "SAUMON FRAIS", "Pavé de saumon frais grillé", 0),
    ("Menu Poissons", "PAELLA ROYALE SUR COMMANDE (MIN 2 PERSONNES)", "Riz safrané, fruits de mer et viandes sur commande", 0),
    ("Menu Enfant", "CHEESE BURGER (V-H 100G)", "Pain brioché, viande hachée 100g, cheddar", 0),
    ("Menu Enfant", "NUGGETS", "Nuggets de poulet croustillants", 0),
    ("Spécialités & Suppléments", "SUPPLÉMENT SAUCE VIANDE (POIVRE/ROQUEFORT/CHAMPIGNONS)", "Au choix : Poivre, Roquefort ou Champignons", 0),
    ("Spécialités & Suppléments", "SUPPLÉMENT SAUCE POISSON (CITRONNÉ/À L'ORANGE/DUGLÉRÉ)", "Au choix : Citronné, à l'Orange ou Dugléré", 0),
]

CATEGORIES = [
    "Menu Pizza",
    "Entrées Froides",
    "Entrées Chaudes",
    "Viandes Blanche",
    "Viandes Rouge",
    "Menu Poissons",
    "Menu Enfant",
    "Spécialités & Suppléments",
]

PAGE_STYLE = """
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: system-ui, -apple-system, "Segoe UI", Tahoma, Arial, sans-serif;
    background-color: #dfece7;
    color: #1f2421;
  }
  .topbar {
    background: #1b1d1c;
    color: #ffffff;
    padding: 18px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 3px solid #c59b27;
  }
  .brand-box {
    margin: 0 auto;
    text-align: center;
  }
  .brand-title {
    font-size: 22px;
    letter-spacing: 3px;
    font-weight: 600;
    margin: 0;
  }
  .brand-sub {
    font-size: 12px;
    color: #d4d8d5;
    margin-top: 2px;
  }
  .table-badge {
    display: inline-block;
    margin-top: 6px;
    padding: 3px 12px;
    border-radius: 999px;
    background: #2f3532;
    color: #f6e7b2;
    font-size: 13px;
    border: 1px solid #c59b27;
  }
  .cat-bar {
    background: #eef4f1;
    padding: 12px 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid #cfd9d4;
  }
  .cat-btn {
    background: #ffffff;
    color: #26322c;
    border: 1px solid #b8c7c0;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
  }
  .cat-btn.active, .cat-btn:hover {
    background: #2c3531;
    color: #ffffff;
    border-color: #2c3531;
  }
  .layout {
    max-width: 1260px;
    margin: 18px auto;
    padding: 0 16px 32px;
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 18px;
    align-items: start;
  }
  @media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; }
  }
  .section-banner {
    background: #333a37;
    color: #ffffff;
    padding: 8px 14px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 10px;
  }
  .dish-card {
    background: #ffffff;
    border: 1px solid #d5ded9;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }
  .dish-name {
    font-weight: 700;
    font-size: 14px;
    color: #1f2623;
    text-transform: uppercase;
  }
  .dish-desc {
    font-size: 12px;
    color: #5a635e;
    margin-top: 3px;
  }
  .dish-price {
    font-size: 12px;
    font-weight: 600;
    color: #374740;
    margin-top: 4px;
  }
  .add-btn {
    background: #2c3531;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
  .add-btn:hover { background: #181e1b; }
  .cart-panel {
    background: #ffffff;
    border: 1px solid #cfd9d4;
    border-radius: 8px;
    padding: 16px;
    position: sticky;
    top: 16px;
  }
  .cart-title {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e3ebe7;
  }
  .cart-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px dashed #e0e8e4;
    font-size: 13px;
    gap: 8px;
  }
  .qty-controls {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .qty-mini {
    background: #e6eeea;
    color: #1f2623;
    border: none;
    border-radius: 4px;
    width: 24px;
    height: 24px;
    font-weight: bold;
    cursor: pointer;
  }
  .total-box {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    font-weight: 700;
    margin: 14px 0;
    padding-top: 10px;
    border-top: 2px solid #d5ded9;
  }
  .submit-order-btn {
    width: 100%;
    background: #1ea34a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 11px 14px;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
  }
  .submit-order-btn:hover { background: #16853b; }
  .clear-btn {
    width: 100%;
    margin-top: 8px;
    background: #f1f5f3;
    color: #374740;
    border: 1px solid #cbd5d0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    cursor: pointer;
  }
  .notice-box {
    max-width: 640px;
    margin: 40px auto;
    background: #ffffff;
    border: 1px solid #cfd9d4;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
  }
  .btn-dark {
    display: inline-block;
    background: #2c3531;
    color: #fff;
    text-decoration: none;
    padding: 9px 18px;
    border-radius: 6px;
    font-size: 14px;
    margin-top: 12px;
  }
</style>
"""


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT 'Selon carte / choix',
            price INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    cols = [r[1] for r in c.execute("PRAGMA table_info(menu_items)").fetchall()]
    if "description" not in cols:
        c.execute("ALTER TABLE menu_items ADD COLUMN description TEXT NOT NULL DEFAULT 'Selon carte / choix'")

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
            "INSERT INTO menu_items (category, name, description, price) VALUES (?, ?, ?, ?)",
            MENU_ITEMS,
        )
    conn.commit()
    conn.close()


def verify_table_request(table_raw: str):
    try:
        table_num = int(table_raw)
    except (ValueError, TypeError):
        return None
    if table_num < 1 or table_num > NUM_TABLES:
        return None
    return table_num


@app.route("/", methods=["GET", "POST"])
def menu():
    init_db()
    if request.method == "POST":
        table_raw = request.form.get("table_num", "").strip()
    else:
        table_raw = request.args.get("table", "").strip()

    table_num = verify_table_request(table_raw)
    if not table_num:
        return (
            f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>PARADISE Restaurant</title>{PAGE_STYLE}</head><body>"
            f"<div class='notice-box'><h2>رقم الطاولة غير صالح.</h2>"
            f"<p>يرجى فتح الرابط مع رقم طاولة صحيح بين 1 و {NUM_TABLES}.</p>"
            f"<a class='btn-dark' href='/?table=1'>فتح الطاولة رقم 1</a></div></body></html>",
            403,
        )

    conn = sqlite3.connect(DB_NAME)
    menu_items = conn.execute(
        "SELECT id, category, name, description, price FROM menu_items ORDER BY id"
    ).fetchall()

    if request.method == "POST":
        chosen = []
        total = 0
        for iid, cat, name, desc, price in menu_items:
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
                f"<!DOCTYPE html><html lang='fr' dir='ltr'><head><meta charset='utf-8'>"
                f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
                f"<title>PARADISE Restaurant - Commande envoyée</title>{PAGE_STYLE}</head><body>"
                f"<div class='notice-box'>"
                f"<h2>Commande envoyée — Table n°{table_num}</h2>"
                f"<p>{summary}</p>"
                f"<a class='btn-dark' href='/?table={table_num}'>Retour au menu</a>"
                f"</div></body></html>"
            )

    conn.close()

    selected_cat = request.args.get("cat", CATEGORIES[0]).strip()
    if selected_cat not in CATEGORIES:
        selected_cat = CATEGORIES[0]

    cat_buttons_html = []
    for cat in CATEGORIES:
        active_cls = "cat-btn active" if cat == selected_cat else "cat-btn"
        cat_buttons_html.append(
            f"<button type='button' class='{active_cls}' onclick=\"selectCategory('{cat.replace(chr(39), '')}', this)\">{cat}</button>"
        )

    cards_html = []
    for iid, cat, name, desc, price in menu_items:
        price_text = f"{price} DA" if price > 0 else "Selon carte / choix"
        display_style = "" if cat == selected_cat else "style='display:none;'"
        safe_name = name.replace("'", "\\'")
        cards_html.append(
            f"<div class='dish-card' data-cat='{cat}' {display_style}>"
            f"<div>"
            f"<div class='dish-name'>{name}</div>"
            f"<div class='dish-desc'>{desc}</div>"
            f"<div class='dish-price'>{price_text}</div>"
            f"</div>"
            f"<button type='button' class='add-btn' onclick=\"addItem({iid}, '{safe_name}', {price})\">+ Ajouter</button>"
            f"</div>"
        )

    hidden_inputs_html = "".join(
        f"<input type='hidden' id='qty_{iid}' name='qty_{iid}' value='0'>"
        for iid, _, _, _, _ in menu_items
    )

    return (
        f"<!DOCTYPE html><html lang='fr' dir='ltr'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>PARADISE Restaurant - Table n°{table_num}</title>{PAGE_STYLE}</head><body>"
        f"<div class='topbar'>"
        f"<div class='brand-box'>"
        f"<div class='brand-title'>PARADISE</div>"
        f"<div class='brand-sub'>Restaurant</div>"
        f"<div class='table-badge'>Table n°{table_num}</div>"
        f"</div>"
        f"<a href='/kitchen' style='color:#fff;text-decoration:none;font-size:13px;background:#2c3531;padding:7px 12px;border-radius:6px;'>Cuisine</a>"
        f"</div>"
        f"<div class='cat-bar'>{''.join(cat_buttons_html)}</div>"
        f"<div class='layout'>"
        f"<div>"
        f"<div id='activeCatBanner' class='section-banner'>{selected_cat}</div>"
        f"<div id='dishesList'>{''.join(cards_html)}</div>"
        f"</div>"
        f"<form method='post' class='cart-panel' onsubmit='return validateOrder()'>"
        f"<input type='hidden' name='table_num' value='{table_num}'>"
        f"{hidden_inputs_html}"
        f"<div class='cart-title'>Panier — Table n°{table_num}</div>"
        f"<div id='cartItems' style='color:#6c7570;font-size:13px;'>Aucun article sélectionné.</div>"
        f"<div class='total-box'><span>TOTAL:</span><span id='cartTotal'>0 DA</span></div>"
        f"<button type='submit' class='submit-order-btn'>Valider & Envoyer en Cuisine</button>"
        f"<button type='button' class='clear-btn' onclick='clearCart()'>Vider le panier</button>"
        f"</form>"
        f"</div>"
        f"<script>"
        f"const cart = {{}};"
        f"function selectCategory(cat, btn) {{"
        f"  document.getElementById('activeCatBanner').textContent = cat;"
        f"  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));"
        f"  if (btn) btn.classList.add('active');"
        f"  document.querySelectorAll('.dish-card').forEach(card => {{"
        f"    card.style.display = (card.getAttribute('data-cat') === cat) ? 'flex' : 'none';"
        f"  }});"
        f"}}"
        f"function addItem(id, name, price) {{"
        f"  if (!cart[id]) cart[id] = {{ name, price, qty: 0 }};"
        f"  cart[id].qty += 1;"
        f"  renderCart();"
        f"}}"
        f"function changeQty(id, delta) {{"
        f"  if (!cart[id]) return;"
        f"  cart[id].qty += delta;"
        f"  if (cart[id].qty <= 0) delete cart[id];"
        f"  renderCart();"
        f"}}"
        f"function clearCart() {{"
        f"  for (const k of Object.keys(cart)) delete cart[k];"
        f"  renderCart();"
        f"}}"
        f"function renderCart() {{"
        f"  document.querySelectorAll(\"input[id^='qty_']\").forEach(inp => inp.value = 0);"
        f"  const container = document.getElementById('cartItems');"
        f"  const keys = Object.keys(cart);"
        f"  let total = 0;"
        f"  if (keys.length === 0) {{"
        f"    container.innerHTML = 'Aucun article sélectionné.';"
        f"    document.getElementById('cartTotal').textContent = '0 DA';"
        f"    return;"
        f"  }}"
        f"  container.innerHTML = '';"
        f"  keys.forEach(id => {{"
        f"    const item = cart[id];"
        f"    const inp = document.getElementById('qty_' + id);"
        f"    if (inp) inp.value = item.qty;"
        f"    total += item.price * item.qty;"
        f"    const row = document.createElement('div');"
        f"    row.className = 'cart-item';"
        f"    row.innerHTML = `<div><b>${{item.name}}</b></div>"
        f"      <div class='qty-controls'>"
        f"        <button type='button' class='qty-mini' onclick='changeQty(${{id}}, -1)'>-</button>"
        f"        <span>${{item.qty}}</span>"
        f"        <button type='button' class='qty-mini' onclick='changeQty(${{id}}, 1)'>+</button>"
        f"      </div>`;"
        f"    container.appendChild(row);"
        f"  }});"
        f"  document.getElementById('cartTotal').textContent = total + ' DA';"
        f"}}"
        f"function validateOrder() {{"
        f"  if (Object.keys(cart).length === 0) {{"
        f"    alert('Veuillez ajouter au moins un plat avant d\\'envoyer.');"
        f"    return false;"
        f"  }}"
        f"  return true;"
        f"}}"
        f"</script></body></html>"
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
        status_label = "En préparation" if status == "pending" else "Prêt"
        btn_html = (
            f"<a class='add-btn' style='text-decoration:none;background:#1ea34a;' href='/kitchen/done/{oid}'>Terminer</a>"
            if status == "pending"
            else f"<span style='color:#1ea34a;font-weight:700;'>✓ Terminé</span>"
        )
        cards.append(
            f"<div class='dish-card' style='display:block;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
            f"<b>Commande #{oid} — Table n°{tnum}</b><span>{status_label}</span></div>"
            f"<p style='margin:8px 0;'>{summary}</p>"
            f"<div>{btn_html}</div></div>"
        )

    body_html = "".join(cards) if cards else "<div class='dish-card'>Aucune commande pour le moment.</div>"

    return (
        f"<!DOCTYPE html><html lang='fr' dir='ltr'><head><meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='5'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>PARADISE - Cuisine</title>{PAGE_STYLE}</head><body>"
        f"<div class='topbar'><div class='brand-box'><div class='brand-title'>PARADISE</div><div class='brand-sub'>Cuisine & Commandes</div></div></div>"
        f"<div style='max-width:900px;margin:20px auto;padding:0 16px;'>{body_html}</div>"
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
