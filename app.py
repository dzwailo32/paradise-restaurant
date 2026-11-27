# -*- coding: utf-8 -*-
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect

app = Flask(__name__)
DB_NAME = "restaurant.db"
NUM_TABLES = 32

MENU_ITEMS = [
    # 1. Menu Pizza
    ("Menu Pizza", "PIZZA MARGHERITA", "Crème fraîche, fromage", 0),
    ("Menu Pizza", "PIZZA CHAMPIGNONS", "Sauce tomate, champignons frais, fromage", 0),
    ("Menu Pizza", "PIZZA VEGETARIENNE", "Sauce tomate, champignons frais, légumes, fromage", 0),
    ("Menu Pizza", "PIZZA CAMPIONE", "Sauce tomate, champignons frais, viande hachée, fromage", 0),
    ("Menu Pizza", "PIZZA ROYALE", "Crème fraîche, poulet, champignons, fromage fumé, poivron, fromage", 0),
    ("Menu Pizza", "PIZZA 4 FROMAGE", "Crème fraîche, assortiment de fromages", 0),
    ("Menu Pizza", "PIZZA NAPOLITANA", "Sauce tomate, anchois, thon, câpres, fromage", 0),
    ("Menu Pizza", "PIZZA CREVETTES", "Crème fraîche, crevettes, fromage", 0),
    ("Menu Pizza", "PIZZA PECHEUR", "Sauce tomate, crevettes, légumes, fromage", 0),
    ("Menu Pizza", "PIZZA FRUITS DE MER", "Sauce tomate, fruits de mer, fromage", 0),
    ("Menu Pizza", "PIZZA PARADISE", "Crème fraîche, saumon fumé, fromage", 0),
    ("Menu Pizza", "PIZZA BURATA", "Sauce tomate, burrata, tomate cerise, sauce pesto", 0),
    ("Menu Pizza", "PIZZA GRAND BLEU", "Sauce tomate, fruits de mer, saumon fumé, fromage", 0),

    # 2. Entrées Froides
    ("Entrées Froides", "SALADE CÉSAR", "", 0),
    ("Entrées Froides", "SALADE VARIÉE", "", 0),
    ("Entrées Froides", "CAMEMBERT FARCIE AUX FRUITS SECS", "", 0),
    ("Entrées Froides", "SALADE DU VIEUX PORT", "", 0),
    ("Entrées Froides", "FRAÎCHEUR PARADISE", "Au choix du chef", 0),
    ("Entrées Froides", "CARPACCIO DE CREVETTE", "", 0),

    # 3. Entrées Chaudes
    ("Entrées Chaudes", "HRIRA", "", 0),
    ("Entrées Chaudes", "SOUPE DE POISSONS", "", 0),
    ("Entrées Chaudes", "BOUREK 2 PCS", "", 0),
    ("Entrées Chaudes", "BESTILLA AU POULET", "", 0),
    ("Entrées Chaudes", "BRIOUTTES AU CREVETTES", "", 0),
    ("Entrées Chaudes", "KHLII (KHLI3)", "", 0),
    ("Entrées Chaudes", "GRATIN DE POULET", "", 0),
    ("Entrées Chaudes", "GRATIN DE CREVETTES", "", 0),
    ("Entrées Chaudes", "CAMEMBERT BBQ ROTI AUX FRUITS SECS ET MIEL", "", 0),
    ("Entrées Chaudes", "CREVETTES SCAMPI SAUCE TARTARE", "", 0),
    ("Entrées Chaudes", "BURGER PARADISE (V-H 200 G)", "", 0),
    ("Entrées Chaudes", "POULPE À LA GALICIENNE", "", 0),

    # 4. Menu Enfant
    ("Menu Enfant", "CHEESE BURGER (V-H 100 G)", "Uniquement pour enfant", 0),
    ("Menu Enfant", "NUGGETS", "Uniquement pour enfant", 0),

    # 5. Viandes Blanche
    ("Viandes Blanche", "BROCHETTE DE POULET (BBQ)", "", 0),
    ("Viandes Blanche", "POULET BIRYANI À L'INDIENNE", "Sauce crémeuse", 0),
    ("Viandes Blanche", "CORDON BLEU", "", 0),
    ("Viandes Blanche", "BALLOTINE DE VOLAILLE", "Aux duxelles de champignons", 0),
    ("Viandes Blanche", "SUPREME DE POULET GRATINÉS", "Aux fruits de mer", 0),

    # 6. Viandes Rouge
    ("Viandes Rouge", "BROCHETTE MIXTE (BBQ)", "", 0),
    ("Viandes Rouge", "STEAK HACHÉE (BBQ)", "Gratiné aux duxelle de champignons", 0),
    ("Viandes Rouge", "COTELETTE D'AGNEAU (BBQ)", "", 0),
    ("Viandes Rouge", "ROULADE DE VEAU", "Sauce chasseur", 0),
    ("Viandes Rouge", "ENTRECÔTE DE VEAU (BBQ)", "Beurre maître d'hôtel", 0),
    ("Viandes Rouge", "FILET DE VEAU (BBQ)", "", 0),
    ("Viandes Rouge", "TADJINE MHAMER", "", 0),
    ("Viandes Rouge", "FOIE DE VEAU", "Sauté - Grillé - En sauce", 0),
    ("Viandes Rouge", "RÔTI D'AGNEAU FARCI AUX FRUITS SEC", "", 0),
    ("Viandes Rouge", "GRILLADES PARADISE (BBQ)", "", 0),
    ("Viandes Rouge", "CÔTE DE VEAU", "", 0),

    # 7. Menu Poissons
    ("Menu Poissons", "CREVETTES GRILLÉES OU SAUTÉES À L'AIL", "", 0),
    ("Menu Poissons", "CREVETTES DÉCORTIQUÉES EN SAUCE", "", 0),
    ("Menu Poissons", "CREVETTES À LA SAUCE DUGLÉRÉ", "", 0),
    ("Menu Poissons", "CALAMARS FRITS OU SAUTÉS À L'AIL", "", 0),
    ("Menu Poissons", "CALAMARS FARCIS", "", 0),
    ("Menu Poissons", "DORADE GRILLÉE (BBQ) OU AU FOUR", "", 0),
    ("Menu Poissons", "MÉLANGE DE POISSONS", "", 0),
    ("Menu Poissons", "MERLAN FRIT, AU FOUR OU PANÉ", "", 0),
    ("Menu Poissons", "LOTTE CARAMÉLISÉE", "", 0),
    ("Menu Poissons", "PAVÉ DE MÉROU", "", 0),
    ("Menu Poissons", "ROULADE DE POISSON EN CROÛTE", "", 0),
    ("Menu Poissons", "ESPADON GRILLÉ (BBQ)", "", 0),
    ("Menu Poissons", "CREVETTES ROYALES", "", 0),
    ("Menu Poissons", "SAUMON FRAIS", "", 0),
    ("Menu Poissons", "MÉLANGE ROYAL", "", 0),
    ("Menu Poissons", "PAELLA ROYALE SUR COMMANDE", "Par personne - Minimum 2 personnes", 0),
    ("Menu Poissons", "PIÈCE DE POISSON SELON DISPONIBILITÉ", "Mérou - Dorade - Langoustes", 0),

    # 8. Spécialités & Suppléments
    ("Spécialités & Suppléments", "SUPPLÉMENT SAUCE VIANDE", "Poivre - Roquefort - Champignons", 0),
    ("Spécialités & Suppléments", "SUPPLÉMENT SAUCE POISSON", "Citronné - À l'orange - Dugléré", 0),
    ("Spécialités & Suppléments", "SPÉCIALITÉS TURQUES SUR COMMANDE", "Hrira, Bourek 1 pc, Salade turque, Viande au gros sel, Dessert et boisson au choix", 0),
]

DISH_IMAGES = {
    "pizza_margherita": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=400&q=80",
    "pizza_seafood": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=400&q=80",
    "pizza_rich": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=400&q=80",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=400&q=80",
    "cheese": "https://images.unsplash.com/photo-1452195100486-9cc805987862?auto=format&fit=crop&w=400&q=80",
    "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=400&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=400&q=80",
    "pastry": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=400&q=80",
    "gratin": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=400&q=80",
    "chicken": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?auto=format&fit=crop&w=400&q=80",
    "steak": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80",
    "tajine": "https://images.unsplash.com/photo-1541518763669-27fef04b14ea?auto=format&fit=crop&w=400&q=80",
    "shrimp": "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=400&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80",
    "paella": "https://images.unsplash.com/photo-1534080564583-6be75777b70a?auto=format&fit=crop&w=400&q=80",
    "sauce": "https://images.unsplash.com/photo-1472476443507-c7a5948772fc?auto=format&fit=crop&w=400&q=80",
}


def get_dish_image(category: str, name: str) -> str:
    n = name.lower()
    c = category.lower()
    if "pizza" in c or "pizza" in n:
        if any(k in n for k in ["crevette", "pecheur", "fruits de mer", "paradise", "grand bleu", "napolitana"]):
            return DISH_IMAGES["pizza_seafood"]
        if any(k in n for k in ["margherita", "4 fromage", "burata"]):
            return DISH_IMAGES["pizza_margherita"]
        return DISH_IMAGES["pizza_rich"]
    if "salade" in n or "fraîcheur" in n:
        return DISH_IMAGES["salad"]
    if "camembert" in n:
        return DISH_IMAGES["cheese"]
    if "carpaccio" in n or "crevette" in n:
        return DISH_IMAGES["shrimp"]
    if "hrira" in n or "soupe" in n:
        return DISH_IMAGES["soup"]
    if "burger" in n:
        return DISH_IMAGES["burger"]
    if "bourek" in n or "bestilla" in n or "brioutte" in n:
        return DISH_IMAGES["pastry"]
    if "gratin" in n:
        return DISH_IMAGES["gratin"]
    if "paella" in n:
        return DISH_IMAGES["paella"]
    if "tadjine" in n or "turques" in n:
        return DISH_IMAGES["tajine"]
    if "sauce" in n:
        return DISH_IMAGES["sauce"]
    if "poisson" in c or any(k in n for k in ["dorade", "merlan", "lotte", "mérou", "espadon", "saumon", "calamar", "poulpe", "poisson"]):
        return DISH_IMAGES["fish"]
    if "blanche" in c or any(k in n for k in ["poulet", "volaille", "cordon bleu", "nuggets"]):
        return DISH_IMAGES["chicken"]
    if "rouge" in c:
        return DISH_IMAGES["steak"]
    return DISH_IMAGES["steak"]


def get_recommendations(category: str, name: str, desc: str):
    text = f"{category} {name} {desc}".lower()
    recs = []

    def add_rec(label):
        if label not in recs:
            recs.append(label)

    if "pizza" in text:
        add_rec("Sans tomate")
        add_rec("Sans oignon")
        add_rec("Bien cuit")
        add_rec("Sans piquant")
        if "champignon" in text or "royale" in text or "campione" in text:
            add_rec("Sans champignons")
    elif "salade" in text or "carpaccio" in text or "fraîcheur" in text or "entrées froides" in text:
        add_rec("Sans salade")
        add_rec("Sauce à part")
        add_rec("Sans oignon")
        add_rec("Sans citron")
    elif "burger" in text:
        add_rec("Sans tomate")
        add_rec("Sans salade")
        add_rec("Sans oignon")
        add_rec("Bien cuit")
    elif any(k in text for k in [
        "viandes", "brochette", "steak", "cotelette", "roulade", "entrecôte",
        "filet", "tadjine", "foie", "rôti", "grillades", "côte de veau",
        "poulet", "cordon bleu", "ballotine", "supreme", "nuggets"
    ]):
        add_rec("Bien cuit")
        add_rec("À point")
        add_rec("Sans sauce")
        add_rec("Sauce à part")
        add_rec("Sans piquant")
    elif any(k in text for k in [
        "poissons", "crevettes", "calamars", "dorade", "merlan", "lotte",
        "mérou", "espadon", "saumon", "paella", "poulpe", "soupe de poissons"
    ]):
        add_rec("Bien cuit")
        add_rec("Citron à part")
        add_rec("Sans ail")
        add_rec("Sans piquant")
    elif "sauce" in text:
        add_rec("À part")
        add_rec("Douce")
        add_rec("Relevée")
    else:
        add_rec("Bien cuit")
        add_rec("Sans piquant")
        add_rec("Sans oignon")
        add_rec("À part")

    return recs[:5]


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, name TEXT NOT NULL, description TEXT DEFAULT '', price REAL NOT NULL)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, table_num TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT '')"
    )
    cols = [r[1] for r in c.execute("PRAGMA table_info(orders)").fetchall()]
    if "created_at" not in cols:
        c.execute("ALTER TABLE orders ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
    c.execute("SELECT COUNT(*) FROM menu")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO menu (category, name, description, price) VALUES (?, ?, ?, ?)",
            MENU_ITEMS,
        )
    conn.commit()
    conn.close()


def get_valid_table(table_raw: str):
    try:
        t = int(str(table_raw).strip())
    except (ValueError, TypeError):
        return None
    if 1 <= t <= NUM_TABLES:
        return str(t)
    return None


def escape_html_attr(val: str) -> str:
    return (
        str(val)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


@app.route("/", methods=["GET", "POST"])
def customer_menu():
    init_db()
    table_raw = request.form.get("table_num") if request.method == "POST" else request.args.get("table", "1")
    table_num = get_valid_table(table_raw)

    if not table_num:
        return """<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PARADISE - Table invalide</title>
<style>
  body { margin:0; font-family:'Segoe UI',Tahoma,sans-serif; background:#eef2f1; color:#24302e; display:flex; align-items:center; justify-content:center; min-height:100vh; padding:16px; }
  .box { background:#fff; border-top:6px solid #586e6b; border-radius:16px; padding:28px 22px; max-width:440px; width:100%; text-align:center; box-shadow:0 10px 28px rgba(36,48,46,0.12); }
  .brand { font-family:Georgia,serif; letter-spacing:4px; color:#586e6b; font-size:26px; font-weight:bold; }
  .btn { display:inline-block; margin-top:14px; background:#586e6b; color:#fff; text-decoration:none; padding:11px 22px; border-radius:10px; font-weight:bold; }
</style>
</head>
<body>
  <div class="box">
    <div class="brand">PARADISE</div>
    <p style="margin-top:14px;">Numéro de table invalide.</p>
    <a class="btn" href="/?table=1">Ouvrir Table 1</a>
  </div>
</body>
</html>""", 403

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        c.execute("SELECT id, name, price FROM menu")
        menu_items = c.fetchall()
        chosen, total = [], 0.0
        for item_id, name, price in menu_items:
            try:
                qty = int(request.form.get(f"qty_{item_id}", 0))
            except (ValueError, TypeError):
                qty = 0
            note = " ".join(request.form.get(f"note_{item_id}", "").strip().split())
            if qty > 0:
                if note:
                    chosen.append(f"{name} (x{qty}) [{note}]")
                else:
                    chosen.append(f"{name} (x{qty})")
                total += price * qty
        if chosen:
            now_str = datetime.now().strftime("%H:%M")
            c.execute(
                "INSERT INTO orders (table_num, items, total, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
                (table_num, " + ".join(chosen), total, now_str),
            )
            conn.commit()
            conn.close()
            items_summary_html = "<br>".join(chosen)
            return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PARADISE - Commande envoyée</title>
<style>
  body {{ margin:0; font-family:'Segoe UI',Tahoma,sans-serif; background:#eef2f1; color:#24302e; display:flex; align-items:center; justify-content:center; min-height:100vh; padding:16px; }}
  .box {{ background:#fff; border-top:6px solid #586e6b; border-radius:16px; padding:28px 22px; max-width:460px; width:100%; text-align:center; box-shadow:0 10px 28px rgba(36,48,46,0.12); }}
  .brand {{ font-family:Georgia,serif; letter-spacing:4px; color:#586e6b; font-size:26px; font-weight:bold; }}
  .sub {{ font-size:13px; color:#6b7d7a; margin-bottom:18px; }}
  .ok {{ background:#e8f0ee; color:#2f4a46; padding:12px; border-radius:10px; font-weight:bold; margin:14px 0; }}
  .recap {{ text-align:left; background:#f7faf9; border:1px solid #dce5e3; border-radius:10px; padding:12px; font-size:13px; line-height:1.5; margin:12px 0; }}
  .btn {{ display:inline-block; margin-top:12px; background:#586e6b; color:#fff; text-decoration:none; padding:12px 24px; border-radius:10px; font-weight:bold; }}
</style>
</head>
<body>
  <div class="box">
    <div class="brand">PARADISE</div>
    <div class="sub">Restaurant</div>
    <div class="ok">✓ Commande envoyée avec succès (Table {table_num})</div>
    <p>Votre commande est en attente de validation par la caisse puis sera préparée en cuisine.</p>
    <div class="recap">{items_summary_html}</div>
    <p><b>Total :</b> {total:.0f} DA</p>
    <a class="btn" href="/?table={table_num}">Retour au menu</a>
  </div>
</body>
</html>"""

    c.execute("SELECT id, category, name, description, price FROM menu ORDER BY id ASC")
    menu_items = c.fetchall()
    conn.close()

    categories = []
    for _, cat, _, _, _ in menu_items:
        if cat not in categories:
            categories.append(cat)

    pills_html = '<button type="button" class="cat-pill active" data-cat="ALL" onclick="selectCategory(\'ALL\', this)">Tout</button>'
    for idx, cat in enumerate(categories):
        cat_key = f"cat_{idx}"
        pills_html += f'<button type="button" class="cat-pill" data-cat="{cat_key}" onclick="selectCategory(\'{cat_key}\', this)">{escape_html_attr(cat)}</button>'

    cat_to_key = {cat: f"cat_{idx}" for idx, cat in enumerate(categories)}
    dishes_payload = {}
    cards_html = ""

    for iid, cat, name, desc, price in menu_items:
        cat_key = cat_to_key[cat]
        price_val = float(price)
        price_label = f"{price_val:.2f} DA" if price_val > 0 else "Selon carte / choix"
        desc_text = desc if desc else "Préparé à la minute par notre chef"
        img_url = get_dish_image(cat, name)
        recs = get_recommendations(cat, name, desc)
        safe_name_attr = escape_html_attr(name)

        dishes_payload[str(iid)] = {
            "id": iid,
            "category": cat,
            "name": name,
            "desc": desc_text,
            "price": price_val,
            "priceLabel": price_label,
            "img": img_url,
            "recs": recs,
        }

        cards_html += f"""
        <article class="dish-card" id="card_{iid}" data-cat="{cat_key}" onclick="openDishModal({iid})">
          <div class="dish-left">
            <img src="{img_url}" alt="{safe_name_attr}" class="dish-thumb" loading="lazy">
            <input type="hidden" name="qty_{iid}" id="qty_{iid}" value="0" data-name="{safe_name_attr}" data-price="{price_val}">
            <input type="hidden" name="note_{iid}" id="note_{iid}" value="">
            <button type="button" class="card-add-btn" id="add_{iid}" onclick="event.stopPropagation(); openDishModal({iid})">AJOUTER</button>
            <div class="card-stepper" id="step_{iid}" style="display:none;" onclick="event.stopPropagation();">
              <button type="button" class="mini-step" onclick="changeQty({iid}, -1)">−</button>
              <span class="mini-num" id="num_{iid}">0</span>
              <button type="button" class="mini-step" onclick="changeQty({iid}, 1)">+</button>
            </div>
          </div>
          <div class="dish-right">
            <h3 class="dish-title">{name}</h3>
            <p class="dish-desc">{desc_text}</p>
            <div class="dish-price">{price_label}</div>
            <div class="dish-cat">Catégorie: {cat}</div>
            <div class="dish-note-tag" id="note_tag_{iid}" style="display:none;"></div>
          </div>
        </article>"""

    dishes_json = json.dumps(dishes_payload, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PARADISE Restaurant — Table {table_num}</title>
<style>
  :root {{
    --sage: #586e6b;
    --sage-dark: #2f403e;
    --navy: #1f3246;
    --sage-light: #e6eeec;
    --bg: #eef2f1;
    --card-bg: #ffffff;
    --text: #1c2726;
    --muted: #5d6d6a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Tahoma, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding-bottom: 96px;
  }}
  .hero {{
    background: linear-gradient(180deg, #586e6b 0%, #3a4c4a 100%);
    color: #fff;
    text-align: center;
    padding: 20px 14px 16px;
  }}
  .hero-frame {{
    border-top: 1.5px solid rgba(255,255,255,0.55);
    border-bottom: 1.5px solid rgba(255,255,255,0.55);
    display: inline-block;
    padding: 6px 24px;
  }}
  .hero h1 {{
    margin: 0;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 26px;
    letter-spacing: 5px;
    font-weight: normal;
  }}
  .hero .sub {{
    font-family: Georgia, serif;
    font-size: 13px;
    letter-spacing: 2px;
    opacity: 0.92;
    margin-top: 2px;
  }}
  .table-pill {{
    display: inline-block;
    margin-top: 10px;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.35);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12.5px;
    font-weight: 600;
  }}

  .cat-bar-wrap {{
    position: sticky;
    top: 10px;
    z-index: 25;
    max-width: 720px;
    margin: 12px auto 6px;
    padding: 0 12px;
  }}
  .cat-bar {{
    background: rgba(62, 78, 76, 0.92);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 10px 12px;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    box-shadow: 0 8px 22px rgba(25, 36, 35, 0.22);
  }}
  .cat-bar::-webkit-scrollbar {{ display: none; }}
  .cat-pill {{
    white-space: nowrap;
    border: none;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    background: rgba(255,255,255,0.82);
    color: #1f2d2b;
    transition: 0.2s;
  }}
  .cat-pill.active {{
    background: var(--navy);
    color: #fff;
    box-shadow: 0 3px 10px rgba(0,0,0,0.22);
  }}

  .container {{
    max-width: 720px;
    margin: 10px auto;
    padding: 0 12px;
  }}
  .cat-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 4px 10px;
    font-size: 14px;
    font-weight: 700;
    color: var(--sage-dark);
  }}

  .dish-card {{
    background: var(--card-bg);
    border-radius: 22px;
    padding: 14px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 14px;
    border: 1.5px solid #dde6e4;
    box-shadow: 0 4px 14px rgba(34, 48, 46, 0.06);
    cursor: pointer;
    transition: transform 0.15s, border-color 0.2s;
  }}
  .dish-card:active {{ transform: scale(0.99); }}
  .dish-card.selected {{
    border-color: var(--navy);
    background: #f7faf9;
  }}
  .dish-left {{
    width: 112px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }}
  .dish-thumb {{
    width: 108px;
    height: 108px;
    border-radius: 18px;
    object-fit: cover;
    background: #dfe7e5;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
  }}
  .card-add-btn {{
    width: 104px;
    background: #eef3f2;
    color: var(--navy);
    border: 1.5px solid var(--navy);
    border-radius: 18px;
    padding: 6px 0;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.4px;
    cursor: pointer;
    transition: 0.2s;
  }}
  .card-add-btn:hover {{
    background: var(--navy);
    color: #fff;
  }}
  .card-stepper {{
    width: 104px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--navy);
    color: #fff;
    border-radius: 18px;
    padding: 4px 8px;
  }}
  .mini-step {{
    background: rgba(255,255,255,0.2);
    border: none;
    color: #fff;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
  }}
  .mini-num {{
    font-size: 13px;
    font-weight: 800;
  }}
  .dish-right {{
    flex: 1;
    min-width: 0;
  }}
  .dish-title {{
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #162120;
    line-height: 1.25;
  }}
  .dish-desc {{
    margin: 5px 0 8px;
    font-size: 13px;
    color: var(--muted);
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .dish-price {{
    font-size: 15px;
    font-weight: 800;
    color: var(--navy);
  }}
  .dish-cat {{
    margin-top: 5px;
    font-size: 12px;
    color: #6b7c79;
  }}
  .dish-note-tag {{
    margin-top: 6px;
    display: inline-block;
    background: #e6eeec;
    color: var(--sage-dark);
    font-size: 11.5px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 10px;
  }}

  /* Bottom Sheet Detail Modal */
  .sheet-bg {{
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 22, 0.55);
    display: none;
    align-items: flex-end;
    justify-content: center;
    z-index: 60;
  }}
  .sheet {{
    background: #fff;
    width: 100%;
    max-width: 620px;
    border-radius: 26px 26px 0 0;
    padding: 18px 20px 24px;
    box-shadow: 0 -10px 30px rgba(0,0,0,0.22);
    max-height: 88vh;
    overflow-y: auto;
  }}
  .sheet-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .sheet-close {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: #eef2f1;
    color: #222;
    font-size: 18px;
    cursor: pointer;
  }}
  .sheet-hero {{
    display: flex;
    gap: 16px;
    align-items: center;
  }}
  .sheet-img {{
    width: 122px;
    height: 122px;
    border-radius: 18px;
    object-fit: cover;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }}
  .sheet-title {{
    margin: 0 0 6px;
    font-size: 18px;
    font-weight: 800;
    color: #162120;
  }}
  .sheet-desc {{
    margin: 0 0 8px;
    font-size: 13.5px;
    color: var(--muted);
    line-height: 1.4;
  }}
  .sheet-price {{
    font-size: 16px;
    font-weight: 800;
    color: var(--navy);
  }}
  .sheet-cat {{
    font-size: 12px;
    color: #6b7c79;
    margin-top: 4px;
  }}
  .sheet-section {{
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid #e6ecea;
  }}
  .sheet-label {{
    font-size: 13px;
    font-weight: 700;
    color: var(--sage-dark);
    margin-bottom: 8px;
  }}
  .rec-chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 10px;
  }}
  .rec-chip {{
    border: 1px solid #c3d1ce;
    background: #f1f6f5;
    color: #263836;
    border-radius: 16px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }}
  .rec-chip.active {{
    background: var(--navy);
    color: #fff;
    border-color: var(--navy);
  }}
  .sheet-note-input {{
    width: 100%;
    padding: 10px 12px;
    border: 1.5px solid #cfd9d7;
    border-radius: 12px;
    font-size: 13.5px;
    font-family: inherit;
  }}
  .sheet-note-input:focus {{
    outline: none;
    border-color: var(--navy);
  }}
  .sheet-qty-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 14px;
  }}
  .sheet-stepper {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: #eef3f2;
    padding: 6px 14px;
    border-radius: 20px;
  }}
  .sheet-step-btn {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: none;
    background: var(--navy);
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
  }}
  .sheet-add-btn {{
    width: 100%;
    margin-top: 16px;
    background: var(--navy);
    color: #fff;
    border: none;
    border-radius: 14px;
    padding: 15px;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.6px;
    cursor: pointer;
  }}

  /* Floating Cart Bar */
  .cart-bar {{
    position: fixed;
    bottom: 14px;
    left: 14px;
    right: 14px;
    max-width: 696px;
    margin: auto;
    background: var(--navy);
    color: #fff;
    padding: 14px 18px;
    border-radius: 16px;
    display: none;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 26px rgba(18, 30, 42, 0.32);
    z-index: 40;
    cursor: pointer;
  }}
  .cart-badge {{
    background: #fff;
    color: var(--navy);
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 12px;
    margin-right: 8px;
  }}

  /* Cart Review Modal */
  .cart-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px dashed #dde5e3;
    gap: 10px;
    font-size: 14px;
  }}
  .cart-note {{
    font-size: 12px;
    color: var(--sage-dark);
    margin-top: 3px;
  }}
</style>
</head>
<body>

<header class="hero">
  <div class="hero-frame">
    <h1>PARADISE</h1>
    <div class="sub">Restaurant</div>
  </div>
  <div><span class="table-pill">Table n° {table_num}</span></div>
</header>

<div class="cat-bar-wrap">
  <nav class="cat-bar" id="catBar">{pills_html}</nav>
</div>

<form method="POST" id="orderForm">
  <input type="hidden" name="table_num" value="{table_num}">
  <main class="container">
    <div class="cat-header">
      <span id="currentCatLabel">Tous les plats</span>
      <span id="visibleCount">{len(menu_items)} plats</span>
    </div>
    <div id="cardsList">{cards_html}</div>
  </main>

  <div class="cart-bar" id="cartBar" onclick="openCart()">
    <div><span class="cart-badge" id="cartCount">0</span> <b>Voir le panier</b></div>
    <div id="cartTotal">0 DA →</div>
  </div>

  <!-- Cart Modal -->
  <div class="sheet-bg" id="cartModal" onclick="if(event.target===this) closeCart()">
    <div class="sheet">
      <div class="sheet-top-bar">
        <h3 style="margin:0;color:var(--navy);">Votre panier — Table {table_num}</h3>
        <button type="button" class="sheet-close" onclick="closeCart()">✕</button>
      </div>
      <div id="cartItems"></div>
      <div style="display:flex;justify-content:space-between;font-weight:800;font-size:16px;margin-top:14px;">
        <span>Total :</span>
        <span id="modalTotal">0 DA</span>
      </div>
      <button type="submit" class="sheet-add-btn">VALIDER ET ENVOYER LA COMMANDE</button>
    </div>
  </div>
</form>

<!-- Dish Details Modal -->
<div class="sheet-bg" id="dishModal" onclick="if(event.target===this) closeDishModal()">
  <div class="sheet">
    <div class="sheet-top-bar">
      <span style="font-size:12.5px;font-weight:700;color:var(--muted);" id="mCatTop"></span>
      <button type="button" class="sheet-close" onclick="closeDishModal()">✕</button>
    </div>
    <div class="sheet-hero">
      <img id="mImg" src="" alt="" class="sheet-img">
      <div>
        <h3 class="sheet-title" id="mTitle"></h3>
        <p class="sheet-desc" id="mDesc"></p>
        <div class="sheet-price" id="mPrice"></div>
        <div class="sheet-cat" id="mCat"></div>
      </div>
    </div>

    <div class="sheet-section">
      <div class="sheet-label">Recommandations / Remarques :</div>
      <div class="rec-chips" id="mRecs"></div>
      <input type="text" class="sheet-note-input" id="mNoteInput" maxlength="140" placeholder="Ajouter une remarque (ex: Sans tomate, Bien cuit...)">
    </div>

    <div class="sheet-qty-row">
      <span style="font-weight:700;font-size:14px;">Quantité :</span>
      <div class="sheet-stepper">
        <button type="button" class="sheet-step-btn" onclick="changeModalQty(-1)">−</button>
        <span id="mQty" style="font-weight:800;font-size:16px;min-width:20px;text-align:center;">1</span>
        <button type="button" class="sheet-step-btn" onclick="changeModalQty(1)">+</button>
      </div>
    </div>

    <button type="button" class="sheet-add-btn" onclick="confirmDishModal()">AJOUTER AU PANIER</button>
  </div>
</div>

<script>
const DISHES = {dishes_json};
let activeDishId = null;
let modalQty = 1;

function escapeText(str) {{
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}

function selectCategory(catKey, btnEl) {{
  document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');

  const cards = document.querySelectorAll('.dish-card');
  let shown = 0;
  cards.forEach(card => {{
    if (catKey === 'ALL' || card.dataset.cat === catKey) {{
      card.style.display = 'flex';
      shown++;
    }} else {{
      card.style.display = 'none';
    }}
  }});

  document.getElementById('currentCatLabel').textContent =
    catKey === 'ALL' ? 'Tous les plats' : btnEl.textContent;
  document.getElementById('visibleCount').textContent =
    shown + (shown === 1 ? ' plat' : ' plats');
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function openDishModal(id) {{
  const dish = DISHES[String(id)];
  if (!dish) return;
  activeDishId = id;

  const existingQty = parseInt(document.getElementById('qty_' + id).value || '0');
  const existingNote = document.getElementById('note_' + id).value || '';
  modalQty = existingQty > 0 ? existingQty : 1;

  document.getElementById('mCatTop').textContent = dish.category;
  document.getElementById('mImg').src = dish.img;
  document.getElementById('mTitle').textContent = dish.name;
  document.getElementById('mDesc').textContent = dish.desc;
  document.getElementById('mPrice').textContent = dish.priceLabel;
  document.getElementById('mCat').textContent = 'Catégorie: ' + dish.category;
  document.getElementById('mQty').textContent = modalQty;
  document.getElementById('mNoteInput').value = existingNote;

  const recsEl = document.getElementById('mRecs');
  recsEl.innerHTML = '';
  (dish.recs || []).forEach(r => {{
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'rec-chip';
    b.textContent = '+ ' + r;
    if (existingNote.toLowerCase().includes(r.toLowerCase())) {{
      b.classList.add('active');
    }}
    b.onclick = () => toggleModalRec(r, b);
    recsEl.appendChild(b);
  }});

  document.getElementById('dishModal').style.display = 'flex';
}}

function closeDishModal() {{
  document.getElementById('dishModal').style.display = 'none';
  activeDishId = null;
}}

function changeModalQty(delta) {{
  modalQty = Math.max(1, Math.min(20, modalQty + delta));
  document.getElementById('mQty').textContent = modalQty;
}}

function toggleModalRec(recText, btn) {{
  const inp = document.getElementById('mNoteInput');
  const parts = inp.value.split(',').map(s => s.trim()).filter(Boolean);
  const idx = parts.findIndex(p => p.toLowerCase() === recText.toLowerCase());
  if (idx >= 0) {{
    parts.splice(idx, 1);
    btn.classList.remove('active');
  }} else {{
    parts.push(recText);
    btn.classList.add('active');
  }}
  inp.value = parts.join(', ');
}}

function confirmDishModal() {{
  if (!activeDishId) return;
  const noteVal = document.getElementById('mNoteInput').value.trim();
  document.getElementById('note_' + activeDishId).value = noteVal;
  setQty(activeDishId, modalQty);
  closeDishModal();
}}

function setQty(id, val) {{
  val = Math.max(0, Math.min(20, val));
  const inp = document.getElementById('qty_' + id);
  inp.value = val;

  const card = document.getElementById('card_' + id);
  const addBtn = document.getElementById('add_' + id);
  const step = document.getElementById('step_' + id);
  const num = document.getElementById('num_' + id);
  const noteInp = document.getElementById('note_' + id);
  const noteTag = document.getElementById('note_tag_' + id);

  if (val > 0) {{
    card.classList.add('selected');
    addBtn.style.display = 'none';
    step.style.display = 'flex';
    num.textContent = val;
    if (noteInp.value.trim()) {{
      noteTag.style.display = 'inline-block';
      noteTag.textContent = 'Note : ' + noteInp.value.trim();
    }} else {{
      noteTag.style.display = 'none';
    }}
  }} else {{
    card.classList.remove('selected');
    addBtn.style.display = 'inline-block';
    step.style.display = 'none';
    noteInp.value = '';
    noteTag.style.display = 'none';
  }}
  updateCart();
}}

function changeQty(id, delta) {{
  const cur = parseInt(document.getElementById('qty_' + id).value || '0');
  setQty(id, cur + delta);
}}

function updateCart() {{
  const inputs = document.querySelectorAll('input[id^="qty_"]');
  let totalCount = 0;
  let totalPrice = 0;
  let html = '';

  inputs.forEach(inp => {{
    const q = parseInt(inp.value || '0');
    if (q > 0) {{
      const id = inp.id.replace('qty_', '');
      const name = inp.dataset.name;
      const price = parseFloat(inp.dataset.price || '0');
      const noteVal = document.getElementById('note_' + id).value.trim();
      totalCount += q;
      totalPrice += q * price;
      const noteHtml = noteVal ? `<div class="cart-note">Note : ${{escapeText(noteVal)}}</div>` : '';
      html += `<div class="cart-row">
        <div><b>${{escapeText(name)}}</b> <small>(×${{q}})</small>${{noteHtml}}</div>
        <div style="white-space:nowrap;">
          <button type="button" onclick="changeQty(${{id}}, -1)" style="padding:3px 9px;">−</button>
          <button type="button" onclick="changeQty(${{id}}, 1)" style="padding:3px 9px;">+</button>
        </div>
      </div>`;
    }}
  }});

  const bar = document.getElementById('cartBar');
  if (totalCount > 0) {{
    bar.style.display = 'flex';
    document.getElementById('cartCount').textContent = totalCount;
    document.getElementById('cartTotal').textContent = totalPrice.toFixed(0) + ' DA →';
    document.getElementById('modalTotal').textContent = totalPrice.toFixed(0) + ' DA';
    document.getElementById('cartItems').innerHTML = html;
  }} else {{
    bar.style.display = 'none';
    closeCart();
  }}
}}

function openCart() {{ document.getElementById('cartModal').style.display = 'flex'; }}
function closeCart() {{ document.getElementById('cartModal').style.display = 'none'; }}
</script>
</body>
</html>"""


@app.route("/cashier")
@app.route("/caisse")
def cashier():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT id, table_num, items, total, status, created_at FROM orders WHERE status IN ('pending', 'approved') ORDER BY id DESC"
    )
    orders = c.fetchall()
    conn.close()

    blocks = []
    for oid, t, items, total, status, created_at in orders:
        time_str = f" · {created_at}" if created_at else ""
        if status == "pending":
            badge = '<span style="background:#fff3cd;color:#856404;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">En attente</span>'
            actions = (
                f'<a href="/cashier/approve/{oid}" style="background:#1ea34a;color:#fff;padding:7px 14px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:700;margin-right:8px;">Valider & Envoyer en Cuisine</a>'
                f'<a href="/cashier/cancel/{oid}" style="background:#f8d7da;color:#842029;padding:7px 12px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;">Annuler</a>'
            )
        else:
            badge = '<span style="background:#d1e7dd;color:#0f5132;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;">Envoyée en cuisine</span>'
            actions = '<span style="color:#586e6b;font-size:13px;font-weight:600;">✓ Transmise à la cuisine</span>'

        blocks.append(
            f'<div style="border-left:5px solid #586e6b;background:#fff;padding:14px;margin:12px 0;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">'
            f'<b>PARADISE | Table {t} — Commande #{oid}<small style="color:#667572;font-weight:normal;">{time_str}</small></b>{badge}</div>'
            f'<p style="margin:10px 0;line-height:1.5;">{items}</p>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">'
            f'<b>Total : {float(total):.0f} DA</b><div>{actions}</div></div></div>'
        )

    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PARADISE - Caisse</title>
</head>
<body style="font-family:'Segoe UI',Tahoma,sans-serif;max-width:860px;margin:auto;padding:18px;background:#f3f6f5;color:#222d2b;">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px;">
    <h2 style="color:#3e504e;margin:0;">PARADISE Restaurant — Caisse</h2>
    <a href="/kitchen" style="background:#586e6b;color:#fff;padding:8px 14px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;">Voir Cuisine →</a>
  </div>
  {''.join(blocks) if blocks else '<div style="background:#fff;padding:18px;border-radius:10px;">Aucune commande en attente ou en cours.</div>'}
</body>
</html>"""


@app.route("/cashier/approve/<int:oid>")
def cashier_approve(oid: int):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE orders SET status='approved' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    return redirect("/cashier")


@app.route("/cashier/cancel/<int:oid>")
def cashier_cancel(oid: int):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE orders SET status='cancelled' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    return redirect("/cashier")


@app.route("/kitchen")
def kitchen():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT id, table_num, items, created_at FROM orders WHERE status='approved' ORDER BY id ASC"
    )
    orders = c.fetchall()
    conn.close()
    blocks = "".join(
        [
            f'<div style="border-left:5px solid #586e6b;background:#fff;padding:12px;margin:10px 0;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.06);">'
            f"<b>PARADISE | Table {t} — Commande #{oid}</b>"
            f"{f' <small style=\"color:#667572;\">({created_at})</small>' if created_at else ''}"
            f"<br><p style='margin:8px 0;line-height:1.5;'>{items}</p>"
            f'<a href="/done/{oid}" style="background:#586e6b;color:#fff;padding:6px 14px;border-radius:6px;text-decoration:none;">Prêt</a></div>'
            for oid, t, items, created_at in orders
        ]
    )
    return (
        f'<html lang="fr" dir="ltr"><head><meta charset="utf-8"><meta http-equiv="refresh" content="5"><title>PARADISE - Cuisine</title></head>'
        f'<body style="font-family:Segoe UI,Tahoma,sans-serif;max-width:800px;margin:auto;padding:18px;background:#f3f6f5;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">'
        f'<h2 style="color:#3e504e;margin:0;">PARADISE Restaurant — Cuisine</h2>'
        f'<a href="/cashier" style="background:#e7eeec;color:#3e504e;border:1px solid #586e6b;padding:7px 13px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;">← Caisse</a>'
        f'</div>{blocks or "<p>Aucune commande pour le moment.</p>"}'
        f"</body></html>"
    )


@app.route("/done/<int:oid>")
def done(oid: int):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE orders SET status='done' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    return redirect("/kitchen")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
