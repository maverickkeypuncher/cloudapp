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

@provider_bp.route('/<int:provider_id>/variables')
def provider_variables(provider_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch provider info
    cursor.execute("SELECT * FROM providers WHERE id = %s", (provider_id,))
    provider = cursor.fetchone()

    if not provider:
        cursor.close()
        return "Provider not found", 404

    # Fetch variables for this provider
    cursor.execute("""
        SELECT id, name, type, value, created_at
        FROM provider_variables
        WHERE provider_id = %s
        ORDER BY created_at DESC
    """, (provider_id,))
    variables = cursor.fetchall()

    cursor.close()

    return render_template(
        'provider_variables.html',
        provider=provider,
        variables=variables
    )

@provider_bp.route('/<int:provider_id>/variables/add', methods=['GET', 'POST'])
def add_provider_variable(provider_id):
    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM providers WHERE id = %s", (provider_id,))
    provider = cursor.fetchone()

    if not provider:
        cursor.close()
        return "Provider not found", 404

    if request.method == 'POST':
        name = request.form.get('name')
        vtype = request.form.get('type')
        value = request.form.get('value')

        cursor.execute("""
            INSERT INTO provider_variables (provider_id, name, type, value)
            VALUES (%s, %s, %s, %s)
        """, (provider_id, name, vtype, value))
        conn.commit()
        cursor.close()

        return redirect(url_for('provider.provider_variables', provider_id=provider_id))

    cursor.close()
    return render_template('provider_variable_add.html', provider=provider)

@provider_bp.route('/variables/<int:var_id>/edit', methods=['GET', 'POST'])
def edit_provider_variable(var_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT pv.*, p.provider_name, p.environment
        FROM provider_variables pv
        JOIN providers p ON pv.provider_id = p.id
        WHERE pv.id = %s
    """, (var_id,))
    var = cursor.fetchone()

    if not var:
        cursor.close()
        return "Variable not found", 404

    if request.method == 'POST':
        name = request.form.get('name')
        value = request.form.get('value')

        cursor.execute("""
            UPDATE provider_variables
            SET name = %s, value = %s
            WHERE id = %s
        """, (name, value, var_id))
        conn.commit()
        cursor.close()

        return redirect(url_for('provider.provider_variables', provider_id=var['provider_id']))

    cursor.close()
    return render_template('provider_variable_edit.html', var=var)

@provider_bp.route('/variables/<int:var_id>/delete', methods=['POST'])
def delete_provider_variable(var_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT provider_id FROM provider_variables WHERE id = %s", (var_id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        return "Variable not found", 404

    provider_id = row['provider_id']

    cursor.execute("DELETE FROM provider_variables WHERE id = %s", (var_id,))
    conn.commit()
    cursor.close()

    return redirect(url_for('provider.provider_variables', provider_id=provider_id))

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
