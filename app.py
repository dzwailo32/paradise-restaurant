# -*- coding: utf-8 -*-
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, jsonify

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


def get_category_badge(cat: str) -> str:
    c = cat.lower()
    if "pizza" in c:
        return "PIZZA"
    if "froides" in c:
        return "FROIDE"
    if "chaudes" in c:
        return "CHAUDE"
    if "enfant" in c:
        return "ENFANT"
    if "blanche" in c:
        return "VOLAILLE"
    if "rouge" in c:
        return "VIANDE"
    if "poisson" in c:
        return "MER"
    return "SPÉCIAL"


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

    grouped = {}
    for iid, cat, name, desc, price in menu_items:
        grouped.setdefault(cat, []).append((iid, name, desc, price))

    cat_cards_html = ""
    dish_sections_html = ""

    for idx, (cat, items) in enumerate(grouped.items()):
        cat_key = f"cat_{idx}"
        badge_txt = get_category_badge(cat)
        cnt_word = "plat" if len(items) == 1 else "plats"

        cat_cards_html += f"""
        <button type="button" class="cat-tile" onclick="openCategory('{cat_key}', {escape_html_attr(json.dumps(cat))})">
          <div class="cat-tile-top">
            <span class="cat-tag">{badge_txt}</span>
            <span class="cat-count">{len(items)} {cnt_word}</span>
          </div>
          <div class="cat-tile-title">{escape_html_attr(cat)}</div>
          <div class="cat-tile-sub">Découvrir la catégorie →</div>
        </button>"""

        rows_html = ""
        for iid, name, desc, price in items:
            price_val = float(price)
            price_label = f"{price_val:.0f} DA" if price_val > 0 else "Selon carte / choix"
            desc_html = f'<div class="item-desc">{desc}</div>' if desc else ""
            safe_name_attr = escape_html_attr(name)
            recs = get_recommendations(cat, name, desc)
            chips_html = "".join(
                f'<button type="button" class="rec-chip" onclick="toggleRec({iid}, {escape_html_attr(json.dumps(r))})">+ {escape_html_attr(r)}</button>'
                for r in recs
            )

            rows_html += f"""
            <div class="item-card" id="card_{iid}">
              <div class="item-top">
                <div class="item-info">
                  <div class="item-title">{name}</div>
                  {desc_html}
                  <div class="item-price">{price_label}</div>
                </div>
                <div class="item-ctrl">
                  <input type="hidden" name="qty_{iid}" id="qty_{iid}" value="0" data-name="{safe_name_attr}" data-price="{price_val}">
                  <button type="button" class="add-btn" id="add_{iid}" onclick="changeQty({iid}, 1)">+ Ajouter</button>
                  <div class="stepper" id="step_{iid}" style="display:none;">
                    <button type="button" class="step-btn" onclick="changeQty({iid}, -1)">−</button>
                    <span class="qty-num" id="num_{iid}">0</span>
                    <button type="button" class="step-btn" onclick="changeQty({iid}, 1)">+</button>
                  </div>
                </div>
              </div>
              <div class="note-box" id="note_box_{iid}" style="display:none;">
                <div class="rec-label">Recommandations :</div>
                <div class="rec-list">{chips_html}</div>
                <input type="text" class="note-input" name="note_{iid}" id="note_{iid}" maxlength="140" placeholder="Note ou remarque (ex: Sans tomate, Bien cuit...)" oninput="updateCart()">
              </div>
            </div>"""

        dish_sections_html += f"""
        <div class="cat-panel" id="panel_{cat_key}" style="display:none;">
          {rows_html}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PARADISE Restaurant — Table {table_num}</title>
<style>
  :root {{
    --sage: #586e6b;
    --sage-dark: #384947;
    --accent: #9b1c2c;
    --sage-light: #e6eeec;
    --bg: #f1f4f3;
    --card: #ffffff;
    --text: #1e2a29;
    --muted: #62726f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Tahoma, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding-bottom: 96px;
  }}

  /* Header */
  .hero {{
    background: linear-gradient(180deg, #586e6b 0%, #3a4c4a 100%);
    color: #fff;
    text-align: center;
    padding: 22px 16px 18px;
    border-bottom: 4px solid #d5dfdd;
  }}
  .hero-welcome {{
    font-size: 13px;
    letter-spacing: 1px;
    opacity: 0.9;
    margin-bottom: 6px;
  }}
  .hero-frame {{
    border-top: 1.5px solid rgba(255,255,255,0.55);
    border-bottom: 1.5px solid rgba(255,255,255,0.55);
    display: inline-block;
    padding: 6px 26px;
  }}
  .hero h1 {{
    margin: 0;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 28px;
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

  .container {{
    max-width: 760px;
    margin: 0 auto;
    padding: 16px 14px;
  }}

  /* Category Grid */
  .cat-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }}
  .cat-tile {{
    background: var(--card);
    border: 1.5px solid #dce5e3;
    border-radius: 20px;
    padding: 16px;
    text-align: left;
    cursor: pointer;
    box-shadow: 0 6px 18px rgba(32, 46, 44, 0.07);
    transition: transform 0.16s, border-color 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 132px;
  }}
  .cat-tile:hover {{
    transform: translateY(-2px);
    border-color: var(--sage);
    box-shadow: 0 10px 22px rgba(32, 46, 44, 0.12);
  }}
  .cat-tile-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }}
  .cat-tag {{
    background: var(--sage-light);
    color: var(--sage-dark);
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.8px;
    padding: 4px 9px;
    border-radius: 10px;
  }}
  .cat-count {{
    font-size: 11.5px;
    color: var(--muted);
    font-weight: 600;
  }}
  .cat-tile-title {{
    font-size: 17px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1.25;
  }}
  .cat-tile-sub {{
    margin-top: 10px;
    font-size: 12px;
    color: var(--sage-dark);
    font-weight: 600;
  }}

  /* Single Category View */
  .cat-topbar {{
    display: none;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    background: #fff;
    border: 1.5px solid #dce5e3;
    border-radius: 14px;
    padding: 10px 14px;
    margin-bottom: 14px;
    position: sticky;
    top: 10px;
    z-index: 25;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  }}
  .back-btn {{
    background: var(--sage-light);
    color: var(--sage-dark);
    border: 1px solid var(--sage);
    border-radius: 10px;
    padding: 7px 12px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
  }}
  .back-btn:hover {{
    background: var(--sage);
    color: #fff;
  }}
  .active-cat-name {{
    font-size: 15px;
    font-weight: 800;
    color: var(--sage-dark);
  }}

  .item-card {{
    background: var(--card);
    border: 1.5px solid #e0e8e6;
    border-radius: 14px;
    padding: 13px 15px;
    margin-bottom: 10px;
    transition: 0.2s;
  }}
  .item-card.selected {{
    border-color: var(--sage);
    background: #f6faf9;
    box-shadow: 0 4px 12px rgba(88,110,107,0.12);
  }}
  .item-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }}
  .item-title {{
    font-weight: 700;
    font-size: 14.5px;
    color: var(--text);
  }}
  .item-desc {{
    font-size: 12px;
    color: var(--muted);
    margin-top: 3px;
    line-height: 1.35;
  }}
  .item-price {{
    font-size: 13px;
    font-weight: 700;
    color: var(--sage-dark);
    margin-top: 5px;
  }}
  .add-btn {{
    background: var(--sage-light);
    color: var(--sage-dark);
    border: 1px solid var(--sage);
    padding: 7px 15px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
  }}
  .add-btn:hover {{
    background: var(--sage);
    color: #fff;
  }}
  .stepper {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--sage);
    color: #fff;
    padding: 4px 8px;
    border-radius: 20px;
  }}
  .step-btn {{
    background: rgba(255,255,255,0.2);
    border: none;
    color: #fff;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
  }}
  .qty-num {{
    font-weight: 800;
    min-width: 18px;
    text-align: center;
    font-size: 14px;
  }}

  .note-box {{
    margin-top: 10px;
    padding-top: 9px;
    border-top: 1px dashed #d5dfdd;
  }}
  .rec-label {{
    font-size: 11.5px;
    color: var(--muted);
    margin-bottom: 6px;
    font-weight: 600;
  }}
  .rec-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }}
  .rec-chip {{
    background: var(--sage-light);
    color: var(--sage-dark);
    border: 1px solid #bfd0cc;
    border-radius: 14px;
    padding: 4px 10px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
  }}
  .rec-chip:hover {{
    background: var(--sage);
    color: #fff;
    border-color: var(--sage);
  }}
  .note-input {{
    width: 100%;
    padding: 8px 11px;
    border: 1px solid #c5d2cf;
    border-radius: 8px;
    font-size: 12.5px;
    font-family: inherit;
    color: var(--text);
    background: #fff;
  }}
  .note-input:focus {{
    outline: none;
    border-color: var(--sage);
  }}

  /* Cart Bar & Modal */
  .cart-bar {{
    position: fixed;
    bottom: 14px;
    left: 14px;
    right: 14px;
    max-width: 732px;
    margin: auto;
    background: var(--sage-dark);
    color: #fff;
    padding: 13px 18px;
    border-radius: 14px;
    display: none;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    z-index: 40;
    cursor: pointer;
  }}
  .cart-badge {{
    background: #fff;
    color: var(--sage-dark);
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 12px;
    margin-right: 8px;
  }}
  .modal-bg {{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: none;
    align-items: flex-end;
    justify-content: center;
    z-index: 50;
  }}
  .modal {{
    background: #fff;
    width: 100%;
    max-width: 600px;
    border-radius: 20px 20px 0 0;
    padding: 20px;
    max-height: 82vh;
    overflow-y: auto;
  }}
  .modal-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e1e8e6;
    padding-bottom: 10px;
    margin-bottom: 12px;
  }}
  .cart-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px dashed #e1e8e6;
    font-size: 14px;
    gap: 10px;
  }}
  .cart-note {{
    font-size: 12px;
    color: var(--sage-dark);
    margin-top: 2px;
  }}
  .confirm-btn {{
    width: 100%;
    background: var(--sage);
    color: #fff;
    border: none;
    padding: 14px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    margin-top: 14px;
    cursor: pointer;
  }}
  .confirm-btn:hover {{
    background: var(--sage-dark);
  }}
</style>
</head>
<body>

<header class="hero">
  <div class="hero-welcome">Bienvenue à</div>
  <div class="hero-frame">
    <h1>PARADISE</h1>
    <div class="sub">Restaurant</div>
  </div>
  <div><span class="table-pill">Table n° {table_num}</span></div>
</header>

<form method="POST" id="orderForm">
  <input type="hidden" name="table_num" value="{table_num}">

  <main class="container">
    <div class="cat-topbar" id="catTopbar">
      <button type="button" class="back-btn" onclick="backToCategories()">← Catégories</button>
      <span class="active-cat-name" id="activeCatTitle"></span>
    </div>

    <div class="cat-grid" id="catGrid">
      {cat_cards_html}
    </div>

    <div id="dishesContainer">
      {dish_sections_html}
    </div>
  </main>

  <div class="cart-bar" id="cartBar" onclick="openCart()">
    <div><span class="cart-badge" id="cartCount">0</span> <b>Voir le panier</b></div>
    <div id="cartTotal">0 DA →</div>
  </div>

  <div class="modal-bg" id="cartModal" onclick="if(event.target===this) closeCart()">
    <div class="modal">
      <div class="modal-head">
        <h3 style="margin:0;color:var(--sage-dark);">Votre panier — Table {table_num}</h3>
        <button type="button" onclick="closeCart()" style="border:none;background:#eee;padding:6px 12px;border-radius:8px;cursor:pointer;">Fermer</button>
      </div>
      <div id="cartItems"></div>
      <div style="display:flex;justify-content:space-between;font-weight:bold;font-size:16px;margin-top:14px;">
        <span>Total :</span>
        <span id="modalTotal">0 DA</span>
      </div>
      <button type="submit" class="confirm-btn">Valider et envoyer la commande</button>
    </div>
  </div>
</form>

<script>
function escapeText(str) {{
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}

function openCategory(catKey, catLabel) {{
  document.getElementById('catGrid').style.display = 'none';
  document.getElementById('catTopbar').style.display = 'flex';
  document.getElementById('activeCatTitle').textContent = catLabel;

  document.querySelectorAll('.cat-panel').forEach(p => {{
    p.style.display = 'none';
  }});
  const target = document.getElementById('panel_' + catKey);
  if (target) target.style.display = 'block';
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function backToCategories() {{
  document.querySelectorAll('.cat-panel').forEach(p => {{
    p.style.display = 'none';
  }});
  document.getElementById('catTopbar').style.display = 'none';
  document.getElementById('catGrid').style.display = 'grid';
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function toggleRec(id, recText) {{
  const noteInp = document.getElementById('note_' + id);
  if (!noteInp) return;
  const parts = noteInp.value
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
  const idx = parts.findIndex(p => p.toLowerCase() === recText.toLowerCase());
  if (idx >= 0) {{
    parts.splice(idx, 1);
  }} else {{
    parts.push(recText);
  }}
  noteInp.value = parts.join(', ');
  updateCart();
}}

function changeQty(id, delta) {{
  const inp = document.getElementById('qty_' + id);
  let val = parseInt(inp.value || '0') + delta;
  if (val < 0) val = 0;
  if (val > 20) val = 20;
  inp.value = val;

  const card = document.getElementById('card_' + id);
  const addBtn = document.getElementById('add_' + id);
  const step = document.getElementById('step_' + id);
  const num = document.getElementById('num_' + id);
  const noteBox = document.getElementById('note_box_' + id);
  const noteInp = document.getElementById('note_' + id);

  if (val > 0) {{
    card.classList.add('selected');
    addBtn.style.display = 'none';
    step.style.display = 'flex';
    num.textContent = val;
    if (noteBox) noteBox.style.display = 'block';
  }} else {{
    card.classList.remove('selected');
    addBtn.style.display = 'inline-block';
    step.style.display = 'none';
    if (noteBox) noteBox.style.display = 'none';
    if (noteInp) noteInp.value = '';
  }}
  updateCart();
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
      const noteEl = document.getElementById('note_' + id);
      const noteVal = noteEl ? noteEl.value.trim() : '';
      totalCount += q;
      totalPrice += q * price;
      const noteHtml = noteVal ? `<div class="cart-note">Note : ${{escapeText(noteVal)}}</div>` : '';
      html += `<div class="cart-row">
        <div><b>${{escapeText(name)}}</b> <small>(×${{q}})</small>${{noteHtml}}</div>
        <div style="white-space:nowrap;">
          <button type="button" onclick="changeQty(${{id}}, -1)" style="padding:2px 8px;">−</button>
          <button type="button" onclick="changeQty(${{id}}, 1)" style="padding:2px 8px;">+</button>
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


@app.route("/api/orders")
def api_orders():
    init_db()
    try:
        since_id = max(0, int(request.args.get("since_id", "0")))
    except (ValueError, TypeError):
        since_id = 0

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT id, table_num, items, total, status, created_at FROM orders WHERE id > ? ORDER BY id ASC",
        (since_id,),
    )
    rows = c.fetchall()
    conn.close()

    data = [
        {
            "remote_id": r[0],
            "table_num": r[1],
            "items": r[2],
            "total": float(r[3]),
            "status": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]
    return jsonify({"orders": data})


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
