from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.simple.simple_routes import simple_routes
from backend.ngos.ngo_routes import ngos
from backend.shared_expenses.shared_expense_routes import shared_expenses
# uncomment these imports as you implement their blueprints and routes
from backend.club_expenses.club_expense_routes import club_expenses
from backend.categories.category_routes import categories
from backend.dashboard_filters.dashboard_filter_routes import dashboard_filters
from backend.analytics.analytics_routes import analytics


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    # app.register_blueprint(simple_routes)
    # app.register_blueprint(ngos, url_prefix="/ngo")

    # based off the REST API matrix, the 4 blueprints are:

    # uncomment these lines as you implement their blueprints and routes
    app.register_blueprint(shared_expenses, url_prefix="/shared-expenses")
    app.register_blueprint(club_expenses, url_prefix="/club-expenses")
    app.register_blueprint(categories, url_prefix="/categories")
    app.register_blueprint(dashboard_filters, url_prefix="/dashboard-filters")
    app.register_blueprint(analytics, url_prefix="/analytics")

    return app
