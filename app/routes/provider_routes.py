from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db_connection

provider_bp = Blueprint("provider", __name__)

@provider_bp.route("/admin/providers", methods=["GET", "POST"])
def admin_providers():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

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
            cursor.execute("""
                INSERT INTO providers (provider_name, environment, url, username, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (provider, environment, url, username, password))
            conn.commit()
            message = "Provider added successfully."
        except Exception as e:
            error = "Provider already exists or error occurred."
        finally:
            cursor.close()
            conn.close()

    return render_template("providers.html", message=message, error=error)


@provider_bp.route("/admin/providers/list")
def providers_list():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM providers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("providers_list.html", providers=rows)


@provider_bp.route("/admin/providers/edit/<int:id>", methods=["GET", "POST"])
def edit_provider(id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM providers WHERE id=%s", (id,))
    provider = cursor.fetchone()

    if not provider:
        return "Provider not found"

    if request.method == "POST":
        cursor.execute("""
            UPDATE providers
            SET provider_name=%s, environment=%s, url=%s, username=%s, password=%s
            WHERE id=%s
        """, (
            request.form.get("provider"),
            request.form.get("environment"),
            request.form.get("url"),
            request.form.get("username"),
            request.form.get("password"),
            id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("provider.providers_list"))

    cursor.close()
    conn.close()
    return render_template("providers_edit.html", provider=provider)


@provider_bp.route("/admin/providers/delete/<int:id>")
def delete_provider(id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM providers WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("provider.providers_list"))
