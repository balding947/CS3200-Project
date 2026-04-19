from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

dashboard_filters = Blueprint("dashboard_filters", __name__)


@dashboard_filters.route("/", methods=["GET"])
def get_all_dashboard_filters():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /dashboard-filters")

        user_id = request.args.get("user_id")
        filter_type = request.args.get("filter_type")
        is_active = request.args.get("is_active")

        query = """
            SELECT
                df.filter_id,
                df.filter_type,
                df.value,
                df.is_active,
                df.user_id,
                u.name AS user_name
            FROM dashboard_filters df
            LEFT JOIN users u
                ON df.user_id = u.user_id
            WHERE 1=1
        """
        params = []

        if user_id:
            query += " AND df.user_id = %s"
            params.append(user_id)

        if filter_type:
            query += " AND df.filter_type = %s"
            params.append(filter_type)

        if is_active is not None and is_active != "":
            query += " AND df.is_active = %s"
            params.append(is_active)

        query += " ORDER BY df.filter_id"

        cursor.execute(query, params)
        filters = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(filters)} dashboard filters")
        return jsonify(filters), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_all_dashboard_filters: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@dashboard_filters.route("/<int:filter_id>", methods=["GET"])
def get_dashboard_filter(filter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /dashboard-filters/{filter_id}")

        cursor.execute("""
            SELECT
                df.filter_id,
                df.filter_type,
                df.value,
                df.is_active,
                df.user_id,
                u.name AS user_name
            FROM dashboard_filters df
            LEFT JOIN users u
                ON df.user_id = u.user_id
            WHERE df.filter_id = %s
        """, (filter_id,))
        dashboard_filter = cursor.fetchone()

        if not dashboard_filter:
            return jsonify({"error": "Dashboard filter not found"}), 404

        return jsonify(dashboard_filter), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_dashboard_filter: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@dashboard_filters.route("/", methods=["POST"])
def create_dashboard_filter():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /dashboard-filters")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        required_fields = ["filter_type", "is_active", "user_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor.execute("""
            INSERT INTO dashboard_filters (
                filter_type,
                value,
                is_active,
                user_id
            )
            VALUES (%s, %s, %s, %s)
        """, (
            data["filter_type"],
            data.get("value"),
            data["is_active"],
            data["user_id"]
        ))

        get_db().commit()

        return jsonify({
            "message": "Dashboard filter created successfully",
            "filter_id": cursor.lastrowid
        }), 201

    except Error as e:
        current_app.logger.error(f"Database error in create_dashboard_filter: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@dashboard_filters.route("/update/<int:filter_id>", methods=["PUT"])
def update_dashboard_filter(filter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /dashboard-filters/update/{filter_id}")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        cursor.execute(
            "SELECT filter_id FROM dashboard_filters WHERE filter_id = %s",
            (filter_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Dashboard filter not found"}), 404

        allowed_fields = ["filter_type", "value", "is_active", "user_id"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(filter_id)

        query = f"""
            UPDATE dashboard_filters
            SET {', '.join(update_fields)}
            WHERE filter_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Dashboard filter updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in update_dashboard_filter: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@dashboard_filters.route("/delete/<int:filter_id>", methods=["DELETE"])
def delete_dashboard_filter(filter_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /dashboard-filters/delete/{filter_id}")

        cursor.execute(
            "SELECT filter_id FROM dashboard_filters WHERE filter_id = %s",
            (filter_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Dashboard filter not found"}), 404

        cursor.execute(
            "DELETE FROM dashboard_filters WHERE filter_id = %s",
            (filter_id,)
        )
        get_db().commit()

        return jsonify({"message": "Dashboard filter deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in delete_dashboard_filter: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()