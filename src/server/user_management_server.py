__author__ = "Frank Kwizera"

from src.shared.server_routes import UserManagementServerRoutes
from flask import jsonify, Flask
from src.get_app import get_app

class UserManagementServer:
    def __init__(self):
        self.app: Flask = get_app()
        self.map_endpoints(app=self.app)

    def map_endpoints(self, app: Flask):
        app.add_url_rule(UserManagementServerRoutes.CREATE_USER, endpoint="create_user", view_func=self.create_user, methods=['GET'])

    def create_user(self):
        return jsonify({'name': 'kwizera frank'})

