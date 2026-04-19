from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
from decimal import Decimal
from datetime import date, datetime

shared_expenses = Blueprint("shared_expenses", __name__)


def serialize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def serialize_row(row):
    return {key: serialize_value(value) for key, value in row.items()}


def serialize_rows(rows):
    return [serialize_row(row) for row in rows]

@shared_expenses.route("/", methods=["GET"])
def get_all_shared_expenses():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /shared-expenses")

        paid_by_user_id = request.args.get("paid_by_user_id")
        category_id = request.args.get("category_id")

        query = """
            SELECT
                se.expense_id,
                se.name,
                se.amount,
                se.date,
                se.paid_by_user_id,
                u.name AS paid_by_name,
                se.category_id,
                c.name AS category_name
            FROM shared_expenses se
            JOIN users u
                ON se.paid_by_user_id = u.user_id
            LEFT JOIN categories c
                ON se.category_id = c.category_id
            WHERE 1=1
        """
        params = []

        if paid_by_user_id:
            query += " AND se.paid_by_user_id = %s"
            params.append(paid_by_user_id)

        if category_id:
            query += " AND se.category_id = %s"
            params.append(category_id)

        query += " ORDER BY se.date DESC, se.expense_id DESC"

        cursor.execute(query, params)
        expenses = serialize_rows(cursor.fetchall())

        current_app.logger.info(f"Retrieved {len(expenses)} shared expenses")
        return jsonify(expenses), 200

    except Error as e:
        current_app.logger.error(f"Error in get_all_shared_expenses: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@shared_expenses.route("/<int:expense_id>", methods=["GET"])
def get_shared_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /shared-expenses/{expense_id}")

        query = """
            SELECT
                se.expense_id,
                se.name,
                se.amount,
                se.date,
                se.paid_by_user_id,
                u.name AS paid_by_name,
                se.category_id,
                c.name AS category_name
            FROM shared_expenses se
            JOIN users u
                ON se.paid_by_user_id = u.user_id
            LEFT JOIN categories c
                ON se.category_id = c.category_id
            WHERE se.expense_id = %s
        """
        cursor.execute(query, (expense_id,))
        expense = cursor.fetchone()

        if not expense:
            return jsonify({"error": "Shared expense not found"}), 404

        cursor.execute("""
            SELECT
                es.split_id,
                es.amount_owed,
                es.is_paid,
                es.user_id,
                u.name AS roommate_name
            FROM expense_splits es
            JOIN users u
                ON es.user_id = u.user_id
            WHERE es.expense_id = %s
            ORDER BY es.split_id
        """, (expense_id,))

        expense = serialize_row(expense)
        expense["splits"] = serialize_rows(cursor.fetchall())

        return jsonify(expense), 200

    except Error as e:
        current_app.logger.error(f"Error in get_shared_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@shared_expenses.route("/", methods=["POST"])
def create_shared_expense():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /shared-expenses")

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["name", "amount", "date", "paid_by_user_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """
            INSERT INTO shared_expenses (
                name,
                amount,
                date,
                paid_by_user_id,
                category_id
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["name"],
            data["amount"],
            data["date"],
            data["paid_by_user_id"],
            data.get("category_id")
        ))

        get_db().commit()
        return jsonify({
            "message": "Shared expense created successfully",
            "expense_id": cursor.lastrowid
        }), 201

    except Error as e:
        current_app.logger.error(f"Error in create_shared_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@shared_expenses.route("/update/<int:expense_id>", methods=["PUT"])
def update_shared_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /shared-expenses/update/{expense_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        cursor.execute(
            "SELECT expense_id FROM shared_expenses WHERE expense_id = %s",
            (expense_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Shared expense not found"}), 404

        allowed_fields = ["name", "amount", "date", "paid_by_user_id", "category_id"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(expense_id)
        query = f"""
            UPDATE shared_expenses
            SET {', '.join(update_fields)}
            WHERE expense_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Shared expense updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in update_shared_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@shared_expenses.route("/delete/<int:expense_id>", methods=["DELETE"])
def delete_shared_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /shared-expenses/delete/{expense_id}")

        cursor.execute(
            "SELECT expense_id FROM shared_expenses WHERE expense_id = %s",
            (expense_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Shared expense not found"}), 404

        cursor.execute("DELETE FROM expense_splits WHERE expense_id = %s", (expense_id,))
        cursor.execute("DELETE FROM shared_expenses WHERE expense_id = %s", (expense_id,))

        get_db().commit()
        return jsonify({"message": "Shared expense deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in delete_shared_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()