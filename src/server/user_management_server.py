__author__ = "Frank Kwizera"

from src.shared.server_routes import UserManagementServerRoutes
from src.storage.database_client import UserDatabaseClient
from src.storage.database_tables import User
from src.server.server_helper import ServerHelper
from src.get_app import get_app
from flask import jsonify, Flask, session, request
from flask_api import status
from typing import Dict


class UserManagementServer:
    def __init__(self):
        self.app: Flask = get_app()
        self.map_endpoints(app=self.app)
        
        # Initiate database clients.
        self.user_database_client: UserDatabaseClient = UserDatabaseClient()

    def map_endpoints(self, app: Flask):
        app.add_url_rule(
            UserManagementServerRoutes.USER_LOGIN, endpoint="user_login",
            view_func=self.user_login, methods=['POST'])

    def user_login(self) -> Dict[str, str]:
        """
        Authenticates the user in the system.
        """
        request_data: Dict[str, str] = request.get_json()
        user_email: str = request_data.get('user_email')
        user_password: str = request_data.get('user_password')

        authenticated_user: User = \
            self.user_database_client.authenticate_user(
                user_email=user_email, user_password=user_password)
        if not authenticated_user:
            return ServerHelper.create_http_response(message="Unable to log in", status=status.HTTP_401_UNAUTHORIZED)

        session['user_uuid'] = authenticated_user.user_uuid
        return jsonify(authenticated_user.to_json_dict())

