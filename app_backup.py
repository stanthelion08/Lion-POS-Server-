from flask import Flask, request, redirect, session
from datetime import datetime
from collections import Counter
import sqlite3

app = Flask(__name__)
app.secret_key = "museum-pos-secret"

def get_db():
    return sqlite3.connect("pos.db")

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bestellingen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tijd TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bestelling_producten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bestelling_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            aantal INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL,
            prijs REAL NOT NULL,
            actief INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM producten")
    aantal_producten = cursor.fetchone()[0]

    if aantal_producten == 0:
        standaard_producten = [
            ("Cola", 2.50),
            ("Fanta", 2.50),
            ("Koffie", 2.00),
            ("Thee", 2.00),
            ("Tosti", 4.50),
            ("Broodje", 3.50),
            ("Entree", 5.00),
            ("Donatie", 1.00)
        ]

    cursor.executemany(
        "INSERT INTO producten (naam, prijs) VALUES (?, ?)",
        standaard_producten
    )

    db.commit()
    db.close()

@app.route("/")
def home():
    return redirect("/kassa")

@app.route("/kassa")
def kassa():
    winkelmand = session.get("winkelmand", [])

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT naam, prijs FROM producten WHERE actief = 1 ORDER BY naam")
    producten = cursor.fetchall()

    db.close()

    html = "<h1>Museum POS</h1>"
    html += "<h2>Producten</h2>"

    for naam, prijs in producten:
        html += f"""
        <form action="/toevoegen" method="post" style="display:inline;">
            <button name="product" value="{naam}">
                {naam}<br>€{prijs:.2f}
            </button>
        </form>
        """

    html += "<h2>Winkelmandje</h2>"

    if winkelmand:
        html += "<ul>"
        for item in winkelmand:
            html += f"<li>{item}</li>"
        html += "</ul>"

        html += """
        <form action="/verstuur" method="post">
            <button type="submit">Bestelling versturen</button>
        </form>

        <form action="/leeg" method="post">
            <button type="submit">Winkelmand leegmaken</button>
        </form>
        """
    else:
        html += "<p>Winkelmandje is leeg.</p>"

    html += '<p><a href="/keuken">Naar keukenscherm</a></p>'

    return html

@app.route("/toevoegen", methods=["POST"])
def toevoegen():
    product = request.form["product"]

    winkelmand = session.get("winkelmand", [])
    winkelmand.append(product)
    session["winkelmand"] = winkelmand

    return redirect("/kassa")

@app.route("/leeg", methods=["POST"])
def leeg():
    session["winkelmand"] = []
    return redirect("/kassa")

@app.route("/verstuur", methods=["POST"])
def verstuur():
    winkelmand = session.get("winkelmand", [])

    if winkelmand:
        db = get_db()
        cursor = db.cursor()

        tijd = datetime.now().strftime("%H:%M")

        cursor.execute(
            "INSERT INTO bestellingen (tijd, status) VALUES (?, ?)",
            (tijd, "Nieuw")
        )

        bestelling_id = cursor.lastrowid
        tellingen = Counter(winkelmand)

        for product, aantal in tellingen.items():
            cursor.execute(
                "INSERT INTO bestelling_producten (bestelling_id, product, aantal) VALUES (?, ?, ?)",
                (bestelling_id, product, aantal)
            )

        db.commit()
        db.close()

    session["winkelmand"] = []
    return redirect("/kassa")

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
    """

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, tijd, status FROM bestellingen WHERE status != 'Klaar' ORDER BY id DESC")
    bestellingen = cursor.fetchall()

    if not bestellingen:
        html += "<p>Geen open bestellingen.</p>"

    for bestelling in bestellingen:
        bestelling_id, tijd, status = bestelling

        html += f"""
        <div style="border:1px solid black; padding:10px; margin:10px;">
            <h2>BON #{bestelling_id}</h2>
            <p>Tijd: {tijd}</p>
            <p>Status: {status}</p>
            <ul>
        """

        cursor.execute(
            "SELECT product, aantal FROM bestelling_producten WHERE bestelling_id = ?",
            (bestelling_id,)
        )

        producten = cursor.fetchall()

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

    html += '<p><a href="/kassa">Terug naar kassa</a></p>'
    html += "</body></html>"

    return html

@app.route("/gereed/<int:bestelling_id>", methods=["POST"])
def gereed(bestelling_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE bestellingen SET status = ? WHERE id = ?",
        ("Klaar", bestelling_id)
    )

    db.commit()
    db.close()

    return redirect("/keuken")

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
