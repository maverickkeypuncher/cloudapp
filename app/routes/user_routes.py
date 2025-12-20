from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection

user_bp = Blueprint("user", __name__)

@user_bp.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.get_json(force=True)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO userrequests 
            (username, project_name, datacenter, cpu, ram, num_servers, storage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session.get("username"),
            data.get("project_name"),
            data.get("datacenter"),
            data.get("cpu"),
            data.get("ram"),
            data.get("num_servers"),
            data.get("storage")
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "ok"})

    return render_template(
        "form.html",
        datacenters=["DUBAI", "ABU DHABI"],
        num_servers_options=list(range(1, 11)),
        storage_options=["100GB", "200GB", "500GB", "1024GB", "2048GB"]
    )


@user_bp.route("/requests")
def requests_page():
    username = session.get("username")
    if not username:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT project_name, datacenter, cpu, ram, num_servers, storage, created_at
        FROM userrequests
        WHERE username = %s
        ORDER BY created_at DESC
    """, (username,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("requests.html", requests=rows, username=username)
