from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

expense_splits = Blueprint("expense_splits", __name__)

@expense_splits.route("/update/<int:split_id>", methods=["PUT"])
def update_expense_split(split_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /expense-splits/update/{split_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        cursor.execute(
            "SELECT split_id FROM expense_splits WHERE split_id = %s",
            (split_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Expense split not found"}), 404

        allowed_fields = ["amount_owed", "is_paid", "user_id"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(split_id)

        query = f"""
            UPDATE expense_splits
            SET {', '.join(update_fields)}
            WHERE split_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Expense split updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in update_expense_split: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()