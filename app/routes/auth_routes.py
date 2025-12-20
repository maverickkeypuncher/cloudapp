from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
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
        except Exception:
            error = "Username already exists"
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html", error=error, success=success)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("user.form"))

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
            session["role"] = row.get("role", "user")
            return redirect(url_for("user.form"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
