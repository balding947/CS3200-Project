from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

categories = Blueprint("categories", __name__)


@categories.route("/", methods=["GET"])
def get_all_categories():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /categories")

        status = request.args.get("status")

        query = """
            SELECT
                category_id,
                name,
                status
            FROM categories
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY category_id"

        cursor.execute(query, params)
        category_list = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(category_list)} categories")
        return jsonify(category_list), 200

    except Error as e:
        current_app.logger.error(f"Error in get_all_categories: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@categories.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /categories/{category_id}")

        cursor.execute("""
            SELECT
                category_id,
                name,
                status
            FROM categories
            WHERE category_id = %s
        """, (category_id,))
        category = cursor.fetchone()

        if not category:
            return jsonify({"error": "Category not found"}), 404

        cursor.execute(
            "SELECT COUNT(*) AS shared_expense_count FROM shared_expenses WHERE category_id = %s",
            (category_id,)
        )
        shared_count = cursor.fetchone()["shared_expense_count"]

        cursor.execute(
            "SELECT COUNT(*) AS club_expense_count FROM club_expenses WHERE category_id = %s",
            (category_id,)
        )
        club_count = cursor.fetchone()["club_expense_count"]

        cursor.execute(
            "SELECT COUNT(*) AS template_count FROM budget_templates WHERE category_id = %s",
            (category_id,)
        )
        template_count = cursor.fetchone()["template_count"]

        category["shared_expense_count"] = shared_count
        category["club_expense_count"] = club_count
        category["budget_template_count"] = template_count

        return jsonify(category), 200

    except Error as e:
        current_app.logger.error(f"Error in get_category: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@categories.route("/", methods=["POST"])
def create_category():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /categories")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        required_fields = ["category_id", "name", "status"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor.execute("""
            INSERT INTO categories (
                category_id,
                name,
                status
            )
            VALUES (%s, %s, %s)
        """, (
            data["category_id"],
            data["name"],
            data["status"]
        ))

        get_db().commit()
        return jsonify({
            "message": "Category created successfully",
            "category_id": data["category_id"]
        }), 201

    except Error as e:
        current_app.logger.error(f"Error in create_category: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@categories.route("/update/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /categories/update/{category_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        cursor.execute(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Category not found"}), 404

        allowed_fields = ["name", "status"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(category_id)

        query = f"""
            UPDATE categories
            SET {', '.join(update_fields)}
            WHERE category_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Category updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in update_category: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@categories.route("/delete/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /categories/delete/{category_id}")

        cursor.execute(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Category not found"}), 404

        cursor.execute(
            "SELECT COUNT(*) AS count_used FROM shared_expenses WHERE category_id = %s",
            (category_id,)
        )
        shared_count = cursor.fetchone()["count_used"]

        cursor.execute(
            "SELECT COUNT(*) AS count_used FROM club_expenses WHERE category_id = %s",
            (category_id,)
        )
        club_count = cursor.fetchone()["count_used"]

        cursor.execute(
            "SELECT COUNT(*) AS count_used FROM budget_templates WHERE category_id = %s",
            (category_id,)
        )
        template_count = cursor.fetchone()["count_used"]

        total_references = shared_count + club_count + template_count

        if total_references > 0:
            return jsonify({
                "error": "Category cannot be deleted because it is still being used",
                "shared_expense_count": shared_count,
                "club_expense_count": club_count,
                "budget_template_count": template_count
            }), 400

        cursor.execute("DELETE FROM categories WHERE category_id = %s", (category_id,))
        get_db().commit()

        return jsonify({"message": "Category deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Error in delete_category: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()