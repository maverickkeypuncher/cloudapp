# app/app.py
#dj

from flask import Flask, render_template, request, redirect, session, url_for
from db import get_db_connection
from mysql.connector import Error


app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"  # for sessions; later we can move this to a Secret too


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role)
            )
            conn.commit()
            success = "User registered successfully!"
        except Exception as e:
            error = "Username already exists"
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html", error=error, success=success)


@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("form"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password, role FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and row["password"] == password:
            session["username"] = username
            #session["role"] = row["role"]
            session["role"] = row.get("role","user")
            return redirect(url_for("form"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/admin/requests")
def admin_request():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM userrequests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("admin_requests.html", requests=rows)

@app.route("/admin/providers/edit/<int:id>", methods=["GET", "POST"])
def edit_provider(id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch existing provider
    cursor.execute("SELECT * FROM providers WHERE id=%s", (id,))
    provider = cursor.fetchone()

    if not provider:
        cursor.close()
        conn.close()
        return "Provider not found"

    if request.method == "POST":
        provider_name = request.form.get("provider")
        environment = request.form.get("environment")
        url = request.form.get("url")
        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute("""
            UPDATE providers 
            SET provider_name=%s, environment=%s, url=%s, username=%s, password=%s
            WHERE id=%s
        """, (provider_name, environment, url, username, password, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("providers_list"))

    cursor.close()
    conn.close()
    return render_template("provider_edit.html", provider=provider)

@app.route("/admin/providers/delete/<int:id>")
def delete_provider(id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM providers WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("providers_list"))

@app.route("/admin/providers/list")
def providers_list():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM providers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("providers_list.html", providers=rows)

@app.route("/admin/providers", methods=["GET", "POST"])
def admin_providers():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

     message = None
    error = None


    if request.method == "POST":
        provider = request.form.get("provider")
        environment = request.form.get("environment")
        url = request.form.get("url")
        username = request.form.get("username")
        password = request.form.get("password")
        try:
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute(
            "INSERT INTO providers (provider_name, environment, url, username, password) VALUES (%s, %s, %s, %s, %s)",
             (provider, environment, url, username, password)

            #"INSERT INTO providers (provider_name, url, username, password) VALUES (%s, %s, %s, %s)",
            #(provider, url, username, password)
        )
        conn.commit()
        message = "Provider added successfully."
        except error as e:
            if e.errno == 1062:
                error = f"{provider} provider already exists for {environment} environment."
            else:
                error = "An error occurred while adding provider."

        finally:
            cursor.close()
            conn.close()

        #return redirect(url_for("admin_providers"))

    return render_template("providers.html",message=message, error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        data = request.get_json(force=True)

        project_name = data.get("project_name")
        datacenter = data.get("datacenter")
        cpu = data.get("cpu")
        ram = data.get("ram")
        num_servers = data.get("num_servers")
        storage = data.get("storage")

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

        return jsonify({"status": "ok"})

    return render_template(
        "form.html",
        datacenters=["DUBAI", "ABU DHABI"],
        num_servers_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        storage_options=["100GB", "200GB", "500GB", "1024GB", "2048GB"]
    )


@app.route("/requests")
def requests_page():
    username = session.get("username")

    if not username:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            project_name,
            datacenter,
            cpu,
            ram,
            num_servers,
            storage,
            created_at
        FROM userrequests
        WHERE username = %s
        ORDER BY created_at DESC
    """, (username,))

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("requests.html", requests=requests, username=username)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
