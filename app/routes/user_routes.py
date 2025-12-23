from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection

user_bp = Blueprint("user", __name__)

@user_bp.route("/openstack", methods=["GET", "POST"])
def openstack():
    if request.method == "POST":
        # Read JSON safely from AJAX
        data = request.get_json(silent=True)
        print("DEBUG JSON RECEIVED (OPENSTACK):", data)

        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        project_name = data.get("project_name")
        volume_size = data.get("volume_size")
        flavor = data.get("flavor")
        no_of_servers = data.get("no_of_servers")
        ostype = data.get("ostype")

        username = session.get("username")

        # Extra safety check
        if not username:
            return jsonify({"status": "error", "message": "User not logged in"}), 401

        conn = get_db_connection()   # same cloudapp DB
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO openstack_requests
            (username, project_name, volume_size, flavor, no_of_servers, ostype)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, project_name, volume_size, flavor, no_of_servers, ostype))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "ok"})

    # GET request → render the OpenStack form
    return render_template(
            "openstack.html",
            no_of_servers=[1,2,3,4,5,6,7,8,9,10],
            ostype = ["Windows Server", "RedHat Linux Server"]
        )

@user_bp.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Read JSON safely from AJAX
        data = request.get_json(silent=True)
        print("DEBUG JSON RECEIVED:", data)

        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        project_name = data.get("project_name")
        datacenter = data.get("datacenter")
        operatingsystem = data.get("os")
        cpu = data.get("cpu")
        ram = data.get("ram")
        num_servers = data.get("num_servers")
        storage = data.get("storage")

        username = session.get("username")

        # Extra safety check
        if not username:
            return jsonify({"status": "error", "message": "User not logged in"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO userrequests 
            (username, project_name, datacenter, operatingsystem, cpu, ram, num_servers, storage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, project_name, datacenter, operatingsystem, cpu, ram, num_servers, storage))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "ok"})

    # GET request → show the form
    return render_template(
        "form.html",
        datacenters=["DUBAI", "ABU DHABI"],
        num_servers_options=[1,2,3,4,5,6,7,8,9,10],
        storage_options=["100GB", "200GB", "500GB", "1024GB", "2048GB"],
        operating_system=["Windows Server","RedHat Enterprise Linux"]
    )


@user_bp.route("/requests")
def requests_page():
    username = session.get("username")

    if not username:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            project_name,
            datacenter,
            operatingsystem,
            cpu,
            ram,
            num_servers,
            storage,
            created_at
        FROM userrequests
        WHERE username = %s
        ORDER BY created_at DESC
    """, (username,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("requests.html", requests=rows, username=username)

@user_bp.route("/cloudrequestform")
def cloudrequestform():
    return render_template("cloudrequestform.html")

