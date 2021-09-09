__author__ = "Frank Kwizera"

from flask_api import status
from flask import jsonify


class ServerHelper:
    @staticmethod
    def create_item_not_found_message(message: str = 'Object not found.'):
        """
        Returns item not found response of the given item.
        """

        return jsonify({'message': message}), status.HTTP_404_NOT_FOUND