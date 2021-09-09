__author__ = "Frank Kwizera"

from flask_api import status
from flask import jsonify, session, wrappers
from typing import Callable
import functools


class ServerHelper:
    @staticmethod
    def login_required(func: Callable):
        """
        Checks if user uuid is stored in the session.
        Inputs:
            - func: Method to be executed after checking if staff id is stored in the session.
        Returns:
            - Throw a 403 error if there is no staff id stored in the session,
              otherwise returns the execution response of the given method.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not session.get('user_uuid'):
                return ServerHelper.create_http_response(
                    message='Login required.',
                    status=status.HTTP_403_FORBIDDEN)

            func_result: Any = func(self, *args, **kwargs)
            return func_result
        return wrapper

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