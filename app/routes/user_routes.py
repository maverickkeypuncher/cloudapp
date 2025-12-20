from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection

user_bp = Blueprint("user", __name__)

@user_bp.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        project_name = request.form.get("project_name")
        datacenter = request.form.get("datacenter")
        cpu = request.form.get("cpu")
        ram = request.form.get("ram")
        num_servers = request.form.get("num_servers")
        storage = request.form.get("storage")

        username = session.get("username")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO userrequests 
        (username, project_name, datacenter, cpu, ram, num_servers, storage)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (username, project_name, datacenter, cpu, ram, num_servers, storage))

        conn.commit()
        cursor.close()
        conn.close()

        return render_template("success.html")

     return render_template(
        "form.html",
        datacenters=["DUBAI", "ABU DHABI"],
        num_servers_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        storage_options=["100GB", "200GB", "500GB", "1024GB", "2048GB"]
     }

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
