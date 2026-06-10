from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database.db"

app = Flask(__name__)
app.secret_key = "RTSTORE_SECRET_FULL"
ADMIN_PASSWORD = "123456"

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        product TEXT,
        email TEXT,
        password TEXT,
        expire TEXT
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO accounts (phone, product, email, password, expire)
    VALUES ('0551234567', 'اشتراك لمدة سنة game pass pc', 'Lanowskin@outlook.com', 'iopiop121212', '2027-06-10')
    """)

    db.commit()
    db.close()

def get_all_accounts():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM accounts ORDER BY id DESC")
    accounts = cur.fetchall()
    db.close()
    return accounts

@app.route("/")
def home():
    return redirect(url_for("login_page"))

@app.route("/gamepass.php")
def gamepass():
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM accounts WHERE phone=?", (phone,))
        account = cur.fetchone()
        db.close()

        if account:
            session["phone"] = phone
            return redirect(url_for("dashboard"))

        error = "🚫 الرقم غير صحيح أو غير سعودي.. الرجاء التأكد أو التواصل مع الدعم."

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "phone" not in session:
        return redirect(url_for("login_page"))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM accounts WHERE phone=?", (session["phone"],))
    account = cur.fetchone()
    db.close()

    if not account:
        session.pop("phone", None)
        return redirect(url_for("login_page"))

    return render_template("dashboard.html", account=account)

@app.route("/logout")
def logout():
    session.pop("phone", None)
    return redirect(url_for("login_page"))

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        error = "كلمة المرور غير صحيحة"
    return render_template("admin_login.html", error=error)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("admin.html", accounts=get_all_accounts(), msg=request.args.get("msg"))

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    phone = request.form.get("phone", "").strip()
    product = request.form.get("product", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    expire = request.form.get("expire", "").strip()

    if not phone or not product or not email or not password:
        return render_template("admin.html", accounts=get_all_accounts(), msg="عبّئ كل الخانات المطلوبة")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM accounts WHERE phone=?", (phone,))
    exists = cur.fetchone()

    if exists:
        cur.execute("""
        UPDATE accounts
        SET product=?, email=?, password=?, expire=?
        WHERE phone=?
        """, (product, email, password, expire, phone))
    else:
        cur.execute("""
        INSERT INTO accounts (phone, product, email, password, expire)
        VALUES (?, ?, ?, ?, ?)
        """, (phone, product, email, password, expire))

    db.commit()
    db.close()

    return redirect(url_for("admin", msg="تم الحفظ بنجاح ويبقى محفوظ حتى بعد إعادة تشغيل الموقع"))

@app.route("/admin/delete/<int:account_id>")
def admin_delete(account_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM accounts WHERE id=?", (account_id,))
    db.commit()
    db.close()

    return redirect(url_for("admin", msg="تم حذف الحساب"))

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    init_db()
app.run(host="192.168.100.19", port=5000, debug=True)
