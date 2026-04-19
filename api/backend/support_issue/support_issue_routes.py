from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

support_issues = Blueprint("support_issues", __name__)

@support_issues.route("/update/<int:issue_id>", methods=["PUT"])
def update_support_issue(issue_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /support-issues/update/{issue_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        cursor.execute(
            "SELECT issue_id FROM support_issues WHERE issue_id = %s",
            (issue_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Support issue not found"}), 404

        allowed_fields = ["description", "status", "submitted_by_user_id"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        if "status" in data:
            valid_statuses = ["open", "in_progress", "resolved", "closed"]
            if data["status"] not in valid_statuses:
                return jsonify({"error": "Invalid status"}), 400

        if "submitted_by_user_id" in data:
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s",
                (data["submitted_by_user_id"],)
            )
            if not cursor.fetchone():
                return jsonify({"error": "User not found"}), 404

        params.append(issue_id)

        query = f"""
            UPDATE support_issues
            SET {', '.join(update_fields)}
            WHERE issue_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Support issue updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in update_support_issue: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()