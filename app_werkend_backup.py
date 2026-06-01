from flask import Flask, request, redirect, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "museum-pos-secret"

TAFELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Bar"]

def get_db():
    return sqlite3.connect("pos.db")

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
    for product in mandje:
        telling[product] = telling.get(product, 0) + 1
    return telling

@app.route("/")
def home():
    return redirect("/kassa")

@app.route("/kassa")
def kassa():
    html = "<h1>Museum POS - Tafels</h1>"

    for tafel in TAFELS:
        html += f"""
        <a href="/tafel/{tafel}">
            <button style="width:120px;height:80px;margin:8px;font-size:24px;">
                Tafel {tafel}
            </button>
        </a>
        """

    html += '<p><a href="/keuken">Keukenscherm</a></p>'
    return html

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

    html = f"<h1>Tafel {tafel}</h1>"
    html += f"<h2>Open bedrag: €{totaal:.2f}</h2>"

    html += "<h2>Product toevoegen</h2>"

    for naam, prijs in producten:
        html += f"""
        <form action="/tafel/{tafel}/toevoegen" method="post" style="display:inline;">
            <button name="product" value="{naam}" style="width:120px;height:70px;margin:5px;">
                {naam}<br>€{prijs:.2f}
            </button>
        </form>
        """

    html += "<h2>Nieuw mandje</h2>"

    if mandje:
        html += "<ul>"
        for product, aantal in mandje_telling.items():
            html += f"<li>{aantal}x {product}</li>"
        html += "</ul>"

        html += f"""
        <form action="/tafel/{tafel}/verstuur" method="post">
            <button style="font-size:22px;padding:12px;">Verstuur naar keuken</button>
        </form>

        <form action="/tafel/{tafel}/leeg" method="post">
            <button>Mandje leegmaken</button>
        </form>
        """
    else:
        html += "<p>Nog geen nieuwe producten gekozen.</p>"

    html += "<h2>Geschiedenis open rekening</h2>"

    if regels:
        html += "<ul>"
        for product, aantal, prijs, tijd in regels:
            html += f"<li>{tijd} - {aantal}x {product} (€{prijs:.2f})</li>"
        html += "</ul>"

        html += f"""
        <form action="/tafel/{tafel}/betaald" method="post">
            <button style="font-size:24px;padding:15px;">Contant betaald</button>
        </form>
        """
    else:
        html += "<p>Geen open rekening.</p>"

    html += '<p><a href="/kassa">Terug naar tafels</a></p>'
    return html

@app.route("/tafel/<tafel>/toevoegen", methods=["POST"])
def tafel_toevoegen(tafel):
    product = request.form["product"]

    key = f"mandje_{tafel}"
    mandje = session.get(key, [])
    mandje.append(product)
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

        for product, aantal in telling.items():
            cursor.execute("SELECT prijs FROM producten WHERE naam = ?", (product,))
            prijs = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO bestelling_producten (bestelling_id, product, aantal, prijs) VALUES (?, ?, ?, ?)",
                (bestelling_id, product, aantal, prijs)
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
    html = """
    <html>
    <head>
    <meta http-equiv="refresh" content="5">
    <title>Keukenscherm</title>
    </head>
    <body>
    <h1>Keukenscherm</h1>

    <div style="
        display:flex;
        flex-wrap:wrap;
        align-items:flex-start;
        gap:10px;
    ">
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
        html += "<p>Geen open keukenbonnen.</p>"

    for bestelling_id, tafel, tijd in bestellingen:
        cursor.execute("""
            SELECT product, aantal
            FROM bestelling_producten
            WHERE bestelling_id = ?
        """, (bestelling_id,))

        producten = cursor.fetchall()

        html += f"""
        <div style="
            border:1px solid black;
            padding:10px;
            width:180px;
            min-height:220px;
            box-sizing:border-box;
            margin-bottom:10px;
        ">
            <h2>Tafel {tafel}</h2>
            <p>{tijd}</p>
            <ul>
        """

        for product, aantal in producten:
            html += f"<li>{aantal}x {product}</li>"

        html += f"""
            </ul>

            <form action="/gereed/{bestelling_id}" method="post">
                <button type="submit">✓ Gereed</button>
            </form>
        </div>
        """

    db.close()

    html += """
    </div>
    <p><a href="/kassa">Terug naar kassa</a></p>
    </body>
    </html>
    """

    return html

@app.route("/gereed/<int:bestelling_id>", methods=["POST"])
def gereed(bestelling_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bestellingen SET status = 'Klaar' WHERE id = ?",
        (bestelling_id,)
    )

    db.commit()
    db.close()

    return redirect("/keuken")

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
