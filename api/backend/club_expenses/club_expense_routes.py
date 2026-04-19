from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
from decimal import Decimal
from datetime import date, datetime

club_expenses = Blueprint("club_expenses", __name__)


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


@club_expenses.route("/", methods=["GET"])
def get_all_club_expenses():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /club-expenses")

        budget_id = request.args.get("budget_id")
        category_id = request.args.get("category_id")
        event_id = request.args.get("event_id")
        needs_reimbursement = request.args.get("needs_reimbursement")

        query = """
            SELECT
                ce.expense_id,
                ce.description,
                ce.amount,
                ce.date,
                ce.receipt_url,
                ce.notes,
                ce.needs_reimbursement,
                ce.paid_by_user_id,
                u.name AS paid_by_name,
                ce.budget_id,
                cb.name AS budget_name,
                ce.category_id,
                c.name AS category_name,
                ce.event_id,
                e.name AS event_name,
                ce.goal_id
            FROM club_expenses ce
            JOIN users u
                ON ce.paid_by_user_id = u.user_id
            JOIN club_budgets cb
                ON ce.budget_id = cb.budget_id
            LEFT JOIN categories c
                ON ce.category_id = c.category_id
            LEFT JOIN events e
                ON ce.event_id = e.event_id
            WHERE 1=1
        """
        params = []

        if budget_id:
            query += " AND ce.budget_id = %s"
            params.append(budget_id)

        if category_id:
            query += " AND ce.category_id = %s"
            params.append(category_id)

        if event_id:
            query += " AND ce.event_id = %s"
            params.append(event_id)

        if needs_reimbursement is not None and needs_reimbursement != "":
            query += " AND ce.needs_reimbursement = %s"
            params.append(needs_reimbursement)

        query += " ORDER BY ce.date DESC, ce.expense_id DESC"

        cursor.execute(query, params)
        expenses = serialize_rows(cursor.fetchall())

        current_app.logger.info(f"Retrieved {len(expenses)} club expenses")
        return jsonify(expenses), 200

    except Error as e:
        current_app.logger.error(f"Error in get_all_club_expenses: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@club_expenses.route("/<int:expense_id>", methods=["GET"])
def get_club_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /club-expenses/{expense_id}")

        query = """
            SELECT
                ce.expense_id,
                ce.description,
                ce.amount,
                ce.date,
                ce.receipt_url,
                ce.notes,
                ce.needs_reimbursement,
                ce.paid_by_user_id,
                u.name AS paid_by_name,
                ce.budget_id,
                cb.name AS budget_name,
                cb.semester,
                cb.total_amount AS budget_total_amount,
                ce.category_id,
                c.name AS category_name,
                ce.event_id,
                e.name AS event_name,
                ce.goal_id
            FROM club_expenses ce
            JOIN users u
                ON ce.paid_by_user_id = u.user_id
            JOIN club_budgets cb
                ON ce.budget_id = cb.budget_id
            LEFT JOIN categories c
                ON ce.category_id = c.category_id
            LEFT JOIN events e
                ON ce.event_id = e.event_id
            WHERE ce.expense_id = %s
        """
        cursor.execute(query, (expense_id,))
        expense = cursor.fetchone()

        if not expense:
            return jsonify({"error": "Club expense not found"}), 404

        cursor.execute("""
            SELECT
                r.reimb_id,
                r.amount,
                r.is_paid,
                r.user_id,
                u.name AS reimbursed_user_name
            FROM reimbursements r
            LEFT JOIN users u
                ON r.user_id = u.user_id
            WHERE r.expense_id = %s
            ORDER BY r.reimb_id
        """, (expense_id,))

        expense = serialize_row(expense)
        expense["reimbursements"] = serialize_rows(cursor.fetchall())

        return jsonify(expense), 200

    except Error as e:
        current_app.logger.error(f"Error in get_club_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@club_expenses.route("/", methods=["POST"])
def create_club_expense():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /club-expenses")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        required_fields = [
            "expense_id",
            "description",
            "amount",
            "date",
            "needs_reimbursement",
            "paid_by_user_id",
            "budget_id"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """
            INSERT INTO club_expenses (
                expense_id,
                description,
                amount,
                date,
                receipt_url,
                notes,
                needs_reimbursement,
                paid_by_user_id,
                budget_id,
                category_id,
                event_id,
                goal_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data["expense_id"],
            data["description"],
            data["amount"],
            data["date"],
            data.get("receipt_url"),
            data.get("notes"),
            data["needs_reimbursement"],
            data["paid_by_user_id"],
            data["budget_id"],
            data.get("category_id"),
            data.get("event_id"),
            data.get("goal_id")
        ))

        get_db().commit()
        return jsonify({
            "message": "Club expense created successfully",
            "expense_id": data["expense_id"]
        }), 201

    except Error as e:
        current_app.logger.error(f"Error in create_club_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@club_expenses.route("/update/<int:expense_id>", methods=["PUT"])
def update_club_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /club-expenses/update/{expense_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        cursor.execute(
            "SELECT expense_id FROM club_expenses WHERE expense_id = %s",
            (expense_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Club expense not found"}), 404

        allowed_fields = [
            "description",
            "amount",
            "date",
            "receipt_url",
            "notes",
            "needs_reimbursement",
            "paid_by_user_id",
            "budget_id",
            "category_id",
            "event_id",
            "goal_id"
        ]

        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(expense_id)
        query = f"""
            UPDATE club_expenses
            SET {', '.join(update_fields)}
            WHERE expense_id = %s
        """

        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Club expense updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in update_club_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@club_expenses.route("/delete/<int:expense_id>", methods=["DELETE"])
def delete_club_expense(expense_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /club-expenses/delete/{expense_id}")

        cursor.execute(
            "SELECT expense_id FROM club_expenses WHERE expense_id = %s",
            (expense_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Club expense not found"}), 404

        cursor.execute("DELETE FROM reimbursements WHERE expense_id = %s", (expense_id,))
        cursor.execute("DELETE FROM club_expenses WHERE expense_id = %s", (expense_id,))

        get_db().commit()
        return jsonify({"message": "Club expense deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in delete_club_expense: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()