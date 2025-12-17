# app/app.py
from flask import Flask, render_template, request, redirect, session, url_for
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"  # for sessions; later we can move this to a Secret too


@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("form"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and row[0] == password:
            session["username"] = username
            return redirect(url_for("form"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/form", methods=["GET", "POST"])
def form():
    if "username" not in session:
        return redirect(url_for("login"))

    datacenters = ["Dubai", "India"]
    num_servers_options = list(range(1, 11))
    storage_options = [f"{i}GB" for i in range(1, 101)]

    if request.method == "POST":
        project_name = request.form.get("project_name")
        datacenter = request.form.get("datacenter")
        cpu = request.form.get("cpu")
        ram = request.form.get("ram")
        num_servers = request.form.get("num_servers")
        storage = request.form.get("storage")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO provisioning_requests
            (project_name, datacenter, cpu, ram, num_servers, storage)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (project_name, datacenter, cpu, ram, num_servers, storage))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("success.html")

    return render_template(
        "form.html",
        datacenters=datacenters,
        num_servers_options=num_servers_options,
        storage_options=storage_options
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
