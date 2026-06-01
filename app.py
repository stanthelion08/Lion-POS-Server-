from flask import Flask, request, redirect, session
from datetime import datetime
import sqlite3
import subprocess

app = Flask(__name__)
app.secret_key = "lion-pos-secret"

TAFELS = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
    "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
    "51", "52", "53", "54", "55", "56", "57", "58", "59", "60",
    "Bar"
]

def get_db():
    return sqlite3.connect("pos.db")

def layout(titel, inhoud):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{titel}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #121212;
                margin: 0;
                padding: 12px;
                color: #f5f5f5;
            }}

            .topbar {{
                background: #000;
                color: #f5c542;
                padding: 14px;
                margin: -12px -12px 15px -12px;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 1px;
            }}

            h1 {{
                font-size: 28px;
                margin-top: 0;
            }}

            h2 {{
                margin-top: 20px;
                color: #f5c542;
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }}

            .tafelkaart {{
                width: 100%;
                height: 95px;
                border: none;
                border-radius: 12px;
                background: #1f1f1f;
                color: #f5f5f5;
                box-shadow: 0 3px 8px rgba(0,0,0,0.5);
                font-size: 22px;
                font-weight: bold;
            }}

            .tafelkaart.open {{
                background: #4a3300;
                color: #ffd66b;
            }}

            .bedrag {{
                display: block;
                font-size: 18px;
                margin-top: 8px;
                font-weight: normal;
            }}

            .paneel {{
                background: #1f1f1f;
                padding: 14px;
                border-radius: 12px;
                box-shadow: 0 2px 7px rgba(0,0,0,0.5);
                margin-bottom: 16px;
            }}

            .groot-bedrag {{
                font-size: 36px;
                font-weight: bold;
                margin: 10px 0;
                color: #ffd66b;
            }}

            .productknop {{
                width: calc(50% - 14px);
                height: 85px;
                margin: 6px;
                border: none;
                border-radius: 10px;
                background: #2a2a2a;
                color: #f5f5f5;
                box-shadow: 0 2px 6px rgba(0,0,0,0.5);
                font-size: 18px;
            }}

            .productknop:active,
            .tafelkaart:active {{
                transform: scale(0.97);
            }}

            .actieknop {{
                width: 100%;
                font-size: 22px;
                padding: 14px 20px;
                border: none;
                border-radius: 10px;
                background: #f5c542;
                color: #111;
                font-weight: bold;
                margin: 5px 0;
            }}

            .sticky-verstuur {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background: #121212;
                padding: 10px;
                box-sizing: border-box;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.5);
            }}

            .sticky-verstuur .actieknop {{
                width: 100%;
                margin: 0;
            }}

            .kleineknop {{
                width: 100%;
                font-size: 18px;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #555;
                background: #2a2a2a;
                color: #f5f5f5;
                margin-top: 6px;
            }}

            .terugknop {{
                width: 100%;
                font-size: 20px;
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #444;
                color: white;
                margin-bottom: 12px;
            }}

            .verwijderknop {{
                font-size: 16px;
                padding: 6px 10px;
                margin-left: 10px;
                border-radius: 6px;
                border: none;
                background: #8b1e1e;
                color: white;
            }}

            input {{
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                margin: 6px 0;
                border-radius: 8px;
                border: 1px solid #555;
                background: #2a2a2a;
                color: #f5f5f5;
                font-size: 18px;
            }}

            ul {{
                font-size: 19px;
                line-height: 1.7;
                padding-left: 22px;
            }}

            li {{
                margin-bottom: 6px;
            }}

            a {{
                color: #ffd66b;
                font-weight: bold;
            }}

            .bonnen {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }}

            .bon {{
                background: #f8f1dc;
                color: #111;
                width: 175px;
                min-height: 230px;
                padding: 12px;
                border-top: 6px solid #111;
                box-shadow: 0 3px 8px rgba(0,0,0,0.6);
                box-sizing: border-box;
            }}

            .bon h2 {{
                font-size: 25px;
                margin: 0 0 8px 0;
                color: #111;
            }}

            .tijd {{
                font-size: 17px;
                margin-bottom: 12px;
            }}

            .productregel {{
                border-bottom: 1px solid #444;
                padding: 12px 0;
            }}

            .status-actief {{
                color: #7CFC90;
                font-weight: bold;
            }}

            .status-uit {{
                color: #ff7777;
                font-weight: bold;
            }}

            @media (min-width: 700px) {{
                body {{
                    padding: 20px;
                }}

                .topbar {{
                    margin: -20px -20px 20px -20px;
                    font-size: 26px;
                }}

                .grid {{
                    grid-template-columns: repeat(4, 160px);
                }}

                .tafelkaart {{
                    height: 110px;
                }}

                .productknop {{
                    width: 145px;
                    height: 90px;
                }}

                .actieknop {{
                    width: auto;
                }}

                .kleineknop {{
                    width: auto;
                }}

                input {{
                    width: auto;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="topbar">Lion POS</div>
        {inhoud}
    </body>
    </html>
    """

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL,
            prijs REAL NOT NULL,
            actief INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bestellingen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tafel TEXT,
            tijd TEXT NOT NULL,
            status TEXT NOT NULL,
            betaald INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bestelling_producten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bestelling_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            aantal INTEGER NOT NULL,
            prijs REAL NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM producten")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO producten (naam, prijs) VALUES (?, ?)",
            [
                ("Cola", 2.50),
                ("Fanta", 2.50),
                ("Koffie", 2.00),
                ("Thee", 2.00),
                ("Tosti", 4.50),
                ("Broodje", 3.50),
                ("Entree", 5.00),
                ("Donatie", 1.00)
            ]
        )

    db.commit()
    db.close()

def get_producten():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT naam, prijs FROM producten WHERE actief = 1 ORDER BY naam")
    producten = cursor.fetchall()
    db.close()
    return producten

def tel_mandje(mandje):
    telling = {}

    for item in mandje:
        sleutel = (
            item["product"],
            item["opmerking"]
        )

        telling[sleutel] = telling.get(sleutel, 0) + 1

    return telling

def open_bedrag_tafel(tafel):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT bp.aantal, bp.prijs
        FROM bestellingen b
        JOIN bestelling_producten bp ON b.id = bp.bestelling_id
        WHERE b.tafel = ? AND b.betaald = 0
    """, (tafel,))

    regels = cursor.fetchall()
    db.close()

    return sum(aantal * prijs for aantal, prijs in regels)

@app.route("/")
def home():
    return redirect("/kassa")

@app.route("/kassa")
def kassa():
    inhoud = "<h1>Tafeloverzicht</h1>"
    inhoud += '<div class="grid">'

    for tafel in TAFELS:
        bedrag = open_bedrag_tafel(tafel)
        open_class = "open" if bedrag > 0 else ""

        inhoud += f"""
        <a href="/tafel/{tafel}">
            <button class="tafelkaart {open_class}">
                Tafel {tafel}
                <span class="bedrag">€{bedrag:.2f}</span>
            </button>
        </a>
        """

    inhoud += "</div>"
    inhoud += '<p style="margin-top:25px;"><a href="/keuken">Keukenscherm openen</a></p>'
    inhoud += '<p><a href="/admin/producten">Productbeheer</a></p>'

    return layout("Lion POS - Kassa", inhoud)

@app.route("/tafel/<tafel>")
def tafel(tafel):
    producten = get_producten()

    key = f"mandje_{tafel}"
    mandje = session.get(key, [])
    mandje_telling = tel_mandje(mandje)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT bp.product, bp.aantal, bp.prijs, b.tijd
        FROM bestellingen b
        JOIN bestelling_producten bp ON b.id = bp.bestelling_id
        WHERE b.tafel = ? AND b.betaald = 0
        ORDER BY b.id ASC
    """, (tafel,))
    regels = cursor.fetchall()

    totaal = sum(aantal * prijs for product, aantal, prijs, tijd in regels)

    db.close()

    inhoud = f"""
    <p>
        <a href="/kassa">
            <button class="terugknop">← Terug naar tafels</button>
        </a>
    </p>

    <h1>Tafel {tafel}</h1>
    """

    inhoud += f"""
    <div class="paneel">
        <h2>Open bedrag</h2>
        <div class="groot-bedrag">€{totaal:.2f}</div>
    </div>
    """

    inhoud += '<div class="paneel">'
    inhoud += "<h2>Product toevoegen</h2>"

    inhoud += """
    <input
        type="text"
        id="productZoeken"
        placeholder="Zoek product..."
        onkeyup="filterProducten()"
        style="margin-bottom:12px;"
    >
    """

    for naam, prijs in producten:
        inhoud += f"""
        <form action="/tafel/{tafel}/toevoegen"
              method="post"
              class="product-form"
              data-product="{naam.lower()}"
              style="display:inline;">

            <input
                type="hidden"
                name="opmerking"
                value=""
                id="opmerking_{naam}">

            <button
                type="submit"
                name="product"
                value="{naam}"
                class="productknop"
                onclick="
                    let opm = prompt('Opmerking voor {naam}:');
                    if(opm !== null){{
                        document.getElementById('opmerking_{naam}').value = opm;
                    }}
                ">
                {naam}<br>€{prijs:.2f}
            </button>

        </form>
        """

    inhoud += "</div>"

    inhoud += '<div class="paneel">'
    inhoud += "<h2>Nieuw mandje</h2>"

    if mandje:
        inhoud += "<ul>"
        for (product, opmerking), aantal in mandje_telling.items():
            inhoud += f"""
            <li>
                {aantal}x {product}
            """

            if opmerking:
                inhoud += f"<br><small>📝 {opmerking}</small>"

            inhoud += f"""
                <form action="/tafel/{tafel}/verwijder"
                      method="post"
                      style="display:inline;">
                    <button
                        name="product"
                        value="{product}"
                        class="verwijderknop">
                        -1
                    </button>
                </form>
            </li>
            """

        inhoud += "</ul>"

        inhoud += f"""
        <form action="/tafel/{tafel}/leeg" method="post">
            <button class="kleineknop">Mandje leegmaken</button>
        </form>

        <div class="sticky-verstuur">
            <form action="/tafel/{tafel}/verstuur" method="post">
                <button class="actieknop">
                    Verstuur naar keuken
                </button>
            </form>
        </div>
        """
    else:
        inhoud += "<p>Nog geen nieuwe producten gekozen.</p>"

    inhoud += "</div>"

    inhoud += '<div class="paneel">'
    inhoud += "<h2>Open rekening</h2>"

    if regels:
        inhoud += "<ul>"
        for product, aantal, prijs, tijd in regels:
            inhoud += f"<li>{tijd} - {aantal}x {product} (€{prijs:.2f})</li>"
        inhoud += "</ul>"

        inhoud += f"""
        <form action="/tafel/{tafel}/betaald" method="post">
            <button class="actieknop">Contant betaald</button>
        </form>
        """
    else:
        inhoud += "<p>Geen open rekening.</p>"

    inhoud += "</div>"
    inhoud += '<div style="height:90px;"></div>'
    inhoud += '<p><a href="/kassa">Terug naar tafels</a></p>'

    inhoud += """
    <script>
    function filterProducten() {
        let zoekterm = document.getElementById("productZoeken").value.toLowerCase();
        let producten = document.getElementsByClassName("product-form");

        for (let i = 0; i < producten.length; i++) {
            let naam = producten[i].getAttribute("data-product");

            if (naam.includes(zoekterm)) {
                producten[i].style.display = "inline";
            } else {
                producten[i].style.display = "none";
            }
        }
    }
    </script>
    """

    return layout(f"Lion POS - Tafel {tafel}", inhoud)

@app.route("/tafel/<tafel>/toevoegen", methods=["POST"])
def tafel_toevoegen(tafel):
    product = request.form["product"]
    opmerking = request.form.get("opmerking", "")

    key = f"mandje_{tafel}"

    mandje = session.get(key, [])

    mandje.append({
        "product": product,
        "opmerking": opmerking
    })

    session[key] = mandje

    return redirect(f"/tafel/{tafel}")

@app.route("/tafel/<tafel>/verwijder", methods=["POST"])
def tafel_verwijder(tafel):
    product = request.form["product"]

    key = f"mandje_{tafel}"
    mandje = session.get(key, [])

    if product in mandje:
        mandje.remove(product)

    session[key] = mandje

    return redirect(f"/tafel/{tafel}")

@app.route("/tafel/<tafel>/leeg", methods=["POST"])
def tafel_leeg(tafel):
    session[f"mandje_{tafel}"] = []
    return redirect(f"/tafel/{tafel}")

@app.route("/tafel/<tafel>/verstuur", methods=["POST"])
def tafel_verstuur(tafel):
    key = f"mandje_{tafel}"
    mandje = session.get(key, [])

    if mandje:
        db = get_db()
        cursor = db.cursor()

        tijd = datetime.now().strftime("%H:%M")

        cursor.execute(
            "INSERT INTO bestellingen (tafel, tijd, status, betaald) VALUES (?, ?, ?, 0)",
            (tafel, tijd, "Nieuw")
        )

        bestelling_id = cursor.lastrowid
        telling = tel_mandje(mandje)

        for (product, opmerking), aantal in telling.items():

            cursor.execute(
                "SELECT prijs FROM producten WHERE naam = ?",
                (product,)
            )

            prijs = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO bestelling_producten
                (
                    bestelling_id,
                    product,
                    aantal,
                    prijs,
                    opmerking
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    bestelling_id,
                    product,
                    aantal,
                    prijs,
                    opmerking
                )
            )

        db.commit()
        db.close()

    session[key] = []
    return redirect(f"/tafel/{tafel}")

@app.route("/tafel/<tafel>/betaald", methods=["POST"])
def tafel_betaald(tafel):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bestellingen SET betaald = 1, status = 'Betaald' WHERE tafel = ? AND betaald = 0",
        (tafel,)
    )

    db.commit()
    db.close()

    return redirect(f"/tafel/{tafel}")

@app.route("/keuken")
def keuken():
    inhoud = """
    <meta http-equiv="refresh" content="5">
    <h1>Keukenscherm</h1>
    <div class="bonnen">
    """

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, tafel, tijd
        FROM bestellingen
        WHERE status = 'Nieuw' AND betaald = 0
        ORDER BY id ASC
    """)

    bestellingen = cursor.fetchall()

    if not bestellingen:
        inhoud += "<p>Geen open keukenbonnen.</p>"

    for bestelling_id, tafel, tijd in bestellingen:
        cursor.execute("""
            SELECT product, aantal, opmerking
            FROM bestelling_producten
            WHERE bestelling_id = ?
        """, (bestelling_id,))

        producten = cursor.fetchall()

        inhoud += f"""
        <div class="bon">
            <h2>Tafel {tafel}</h2>
            <div class="tijd">{tijd}</div>
            <ul>
        """

        for product, aantal, opmerking in producten:
            inhoud += f"<li>{aantal}x {product}"

            if opmerking:
                inhoud += f"<br><small>📝 {opmerking}</small>"

            inhoud += "</li>"

        inhoud += f"""
            </ul>

            <form action="/gereed/{bestelling_id}" method="post">
                <button class="kleineknop">✓ Gereed</button>
            </form>
        </div>
        """

    db.close()

    inhoud += "</div>"
    inhoud += '<p style="margin-top:25px;"><a href="/kassa">Terug naar kassa</a></p>'

    return layout("Lion POS - Keukenscherm", inhoud)

def print_bon(bestelling_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT tafel, tijd
            FROM bestellingen
            WHERE id = ?
        """, (bestelling_id,))
        bestelling = cursor.fetchone()

        if not bestelling:
            db.close()
            return

        tafel, tijd = bestelling

        cursor.execute("""
            SELECT product, aantal, opmerking
            FROM bestelling_producten
            WHERE bestelling_id = ?
        """, (bestelling_id,))
        producten = cursor.fetchall()

        db.close()

        bon = ""
        bon += "LION POS\n"
        bon += "------------------------\n"
        bon += f"Tafel: {tafel}\n"
        bon += f"Tijd: {tijd}\n"
        bon += "------------------------\n"

        for product, aantal, opmerking in producten:
            bon += f"{aantal}x {product}\n"
            if opmerking:
                bon += f"  Opmerking: {opmerking}\n"

        bon += "------------------------\n"
        bon += "Gereed\n\n\n"

        subprocess.run(
            ["lp"],
            input=bon.encode("utf-8"),
            timeout=3,
            check=False
        )

    except Exception:
        pass

@app.route("/gereed/<int:bestelling_id>", methods=["POST"])
def gereed(bestelling_id):

    print_bon(bestelling_id)

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bestellingen SET status = 'Klaar' WHERE id = ?",
        (bestelling_id,)
    )

    db.commit()
    db.close()

    return redirect("/keuken")

@app.route("/admin/producten")
def admin_producten():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, naam, prijs, actief FROM producten ORDER BY naam")
    producten = cursor.fetchall()

    db.close()

    inhoud = "<h1>Productbeheer</h1>"

    inhoud += """
    <div class="paneel">
        <h2>Nieuw product</h2>
        <form action="/admin/producten/toevoegen" method="post">
            <input name="naam" placeholder="Productnaam" required>
            <input name="prijs" placeholder="Prijs, bijv. 2.50" required>
            <button class="actieknop">Toevoegen</button>
        </form>
    </div>
    """

    inhoud += '<div class="paneel"><h2>Bestaande producten</h2>'

    for product_id, naam, prijs, actief in producten:
        status_tekst = "Actief" if actief else "Uitgeschakeld"
        status_class = "status-actief" if actief else "status-uit"
        knop_tekst = "Uitschakelen" if actief else "Inschakelen"

        inhoud += f"""
        <div class="productregel">
            <form action="/admin/producten/{product_id}/update" method="post">
                <input name="naam" value="{naam}" required>
                <input name="prijs" value="{prijs:.2f}" required>
                <button class="kleineknop">Opslaan</button>
            </form>

            <p>Status: <span class="{status_class}">{status_tekst}</span></p>

            <form action="/admin/producten/{product_id}/toggle" method="post">
                <button class="kleineknop">{knop_tekst}</button>
            </form>
        </div>
        """

    inhoud += "</div>"
    inhoud += '<p><a href="/kassa">Terug naar kassa</a></p>'

    return layout("Lion POS - Productbeheer", inhoud)

@app.route("/admin/producten/toevoegen", methods=["POST"])
def admin_product_toevoegen():
    naam = request.form["naam"].strip()
    prijs = float(request.form["prijs"].replace(",", "."))

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO producten (naam, prijs, actief) VALUES (?, ?, 1)",
        (naam, prijs)
    )

    db.commit()
    db.close()

    return redirect("/admin/producten")

@app.route("/admin/producten/<int:product_id>/update", methods=["POST"])
def admin_product_update(product_id):
    naam = request.form["naam"].strip()
    prijs = float(request.form["prijs"].replace(",", "."))

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE producten SET naam = ?, prijs = ? WHERE id = ?",
        (naam, prijs, product_id)
    )

    db.commit()
    db.close()

    return redirect("/admin/producten")

@app.route("/admin/producten/<int:product_id>/toggle", methods=["POST"])
def admin_product_toggle(product_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT actief FROM producten WHERE id = ?", (product_id,))
    actief = cursor.fetchone()[0]

    nieuw = 0 if actief else 1

    cursor.execute(
        "UPDATE producten SET actief = ? WHERE id = ?",
        (nieuw, product_id)
    )

    db.commit()
    db.close()

    return redirect("/admin/producten")

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
