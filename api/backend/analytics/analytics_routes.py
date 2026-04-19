from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error
from decimal import Decimal

analytics = Blueprint("analytics", __name__)


def serialize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_row(row):
    return {key: serialize_value(value) for key, value in row.items()}


def serialize_rows(rows):
    return [serialize_row(row) for row in rows]


@analytics.route("/spending-by-category", methods=["GET"])
def spending_by_category():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /analytics/spending-by-category")

        cursor.execute("""
            SELECT
                c.name AS category_name,
                SUM(t.amount) AS total_spent
            FROM (
                SELECT category_id, amount FROM shared_expenses
                UNION ALL
                SELECT category_id, amount FROM club_expenses
            ) AS t
            JOIN categories c ON t.category_id = c.category_id
            GROUP BY c.category_id, c.name
            ORDER BY total_spent DESC
        """)
        results = serialize_rows(cursor.fetchall())
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Error in spending_by_category: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/spending-trends", methods=["GET"])
def spending_trends():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /analytics/spending-trends")

        cursor.execute("""
            SELECT
                DATE_FORMAT(t.expense_date, '%Y-%m') AS month,
                SUM(t.amount) AS total_spent
            FROM (
                SELECT date AS expense_date, amount FROM shared_expenses
                UNION ALL
                SELECT date AS expense_date, amount FROM club_expenses
            ) AS t
            GROUP BY DATE_FORMAT(t.expense_date, '%Y-%m')
            ORDER BY month
        """)
        results = serialize_rows(cursor.fetchall())
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Error in spending_trends: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/student-group-spending", methods=["GET"])
def student_group_spending():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /analytics/student-group-spending")

        housing_type = request.args.get("housing_type")
        class_year = request.args.get("class_year")

        query = """
            SELECT
                u.housing_type,
                u.class_year,
                c.name AS category_name,
                SUM(se.amount) AS total_spent
            FROM shared_expenses se
            JOIN users u
                ON se.paid_by_user_id = u.user_id
            LEFT JOIN categories c
                ON se.category_id = c.category_id
            WHERE 1=1
        """
        params = []

        if housing_type:
            query += " AND u.housing_type = %s"
            params.append(housing_type)

        if class_year:
            query += " AND u.class_year = %s"
            params.append(class_year)

        query += """
            GROUP BY u.housing_type, u.class_year, c.name
            ORDER BY u.class_year, u.housing_type, total_spent DESC
        """

        cursor.execute(query, params)
        results = serialize_rows(cursor.fetchall())
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Error in student_group_spending: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/shared-expense-patterns", methods=["GET"])
def shared_expense_patterns():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /analytics/shared-expense-patterns")

        housing_type = request.args.get("housing_type")
        class_year = request.args.get("class_year")

        query = """
            SELECT
                u.housing_type,
                u.class_year,
                c.name AS category_name,
                COUNT(DISTINCT se.expense_id) AS total_expenses,
                COUNT(DISTINCT se.paid_by_user_id) AS unique_payers,
                AVG(es.amount_owed) AS avg_split_amount,
                SUM(se.amount) AS total_spent,
                SUM(CASE WHEN es.is_paid = 0 THEN es.amount_owed ELSE 0 END) AS total_unpaid
            FROM shared_expenses se
            JOIN users u
                ON se.paid_by_user_id = u.user_id
            LEFT JOIN categories c
                ON se.category_id = c.category_id
            LEFT JOIN expense_splits es
                ON se.expense_id = es.expense_id
            WHERE 1=1
        """
        params = []

        if housing_type:
            query += " AND u.housing_type = %s"
            params.append(housing_type)

        if class_year:
            query += " AND u.class_year = %s"
            params.append(class_year)

        query += """
            GROUP BY u.housing_type, u.class_year, c.name
            ORDER BY u.class_year, u.housing_type, total_spent DESC
        """

        cursor.execute(query, params)
        results = serialize_rows(cursor.fetchall())
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Error in shared_expense_patterns: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@analytics.route("/support-issues", methods=["GET"])
def support_issues():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /analytics/support-issues")

        status = request.args.get("status")

        query = """
            SELECT
                si.issue_id,
                si.description,
                si.status,
                si.created_at,
                u.name AS submitted_by
            FROM support_issues si
            LEFT JOIN users u
                ON si.submitted_by_user_id = u.user_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND si.status = %s"
            params.append(status)

        query += " ORDER BY si.created_at DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        for row in results:
            if row.get("created_at"):
                row["created_at"] = row["created_at"].isoformat()

        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Error in support_issues: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()