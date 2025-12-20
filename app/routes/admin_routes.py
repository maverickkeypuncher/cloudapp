from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/requests")
def admin_request():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM userrequests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("admin_requests.html", requests=rows)
