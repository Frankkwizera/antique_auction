__author__ = "Frank Kwizera"

from flask_api import status
from flask import jsonify, session, wrappers
from typing import Callable
import functools


class ServerHelper:
    @staticmethod
    def create_item_not_found_message(message: str = 'Object not found.') -> wrappers.Response:
        """
        Creates and return item not found response.
        Inputs:
            - message: Desired message.
        Returns
            - Json response indicating that the item is not found.
        """
        return jsonify({'message': message}), status.HTTP_404_NOT_FOUND
    
    @staticmethod
    def create_http_response(message: str, status: status) -> wrappers.Response:
        """
        Creates and return an http response.
        Inputs:
            - message: Desire response message.
            - status: Desire response status.
        Returns
            - Json response indicating that the item is not found.
        """
        return jsonify({'message': message}), status