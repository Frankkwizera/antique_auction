__author__ = "Frank Kwizera"

from src.server.bid_management import BidManagementServer
from src.storage.database_provider import db_provider
from src.storage.database_client import UserDatabaseClient, ItemDatabaseClient
from src.storage.database_tables import User, Item
from src.shared.server_routes import BidManagementServerRoutes
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask.testing import FlaskClient
from flask import Flask
from src.get_app import get_app
import unittest
from typing import Dict
import uuid
import datetime
import json
import unittest


db: SQLAlchemy = db_provider.db


class BidManagementServerTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.app: Flask = get_app()
        cls.client: FlaskClient = cls.app.test_client() 
        cls.app.app_context().push()

        cls.bid_management_server: BidManagementServer = BidManagementServer()
        cls.user_database_client: UserDatabaseClient = UserDatabaseClient()
        cls.item_database_client: ItemDatabaseClient = ItemDatabaseClient()

        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_register_auto_bid(self):
        bidder_uuid: str = str(uuid.uuid4())
        bid_item_uuid: str = str(uuid.uuid4())
        auto_bid_params: Dict[str, str] = {
            'bid_item_uuid': bid_item_uuid,
            'bidder_uuid': bidder_uuid
        }

        register_auto_bid_response: Response = self.client.post(
            BidManagementServerRoutes.REGISTER_AUTO_BID, json=auto_bid_params)
        self.assertEqual(register_auto_bid_response.status_code, 404)

        register_auto_bid_json_response: Dict[str, str] = json.loads(register_auto_bid_response.data)
        self.assertEqual(register_auto_bid_json_response['message'], f'User with uuid {bidder_uuid} does not exists.')

        # Register user.
        new_user: User = self.user_database_client.create_and_save_new_user(
            user_names='Frank Kwizera', 
            user_email='frank@gmail.com', 
            user_password='frank@1235')

        auto_bid_params: Dict[str, str] = {
            'bid_item_uuid': bid_item_uuid,
            'bidder_uuid': new_user.user_uuid
        }

        register_auto_bid_response: Response = self.client.post(
            BidManagementServerRoutes.REGISTER_AUTO_BID, json=auto_bid_params)
        self.assertEqual(register_auto_bid_response.status_code, 404)

        register_auto_bid_json_response: Dict[str, str] = json.loads(register_auto_bid_response.data)
        self.assertEqual(register_auto_bid_json_response['message'], f'Item with uuid {bid_item_uuid} does not exists.')

        item_details: Dict[str, Union[str, int]] = {
            'item_name': 'Item 1', 
            'item_description': 'Item 1 description',
            'item_base_price_in_usd': 250,
            'item_owner_uuid': new_user.user_uuid,
            'bid_expiration_timestamp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        item_record: Item = self.item_database_client.create_and_save_new_item(**item_details)

        auto_bid_params: Dict[str, str] = {
            'bid_item_uuid': item_record.item_uuid,
            'bidder_uuid': new_user.user_uuid
        }

        register_auto_bid_response: Response = self.client.post(
            BidManagementServerRoutes.REGISTER_AUTO_BID, json=auto_bid_params)
        self.assertEqual(register_auto_bid_response.status_code, 200)

        register_auto_bid_json_response: Dict[str, str] = json.loads(register_auto_bid_response.data)
        self.assertEqual(register_auto_bid_json_response['bid_item_uuid'], item_record.item_uuid)
        self.assertEqual(register_auto_bid_json_response['bidder_uuid'], new_user.user_uuid)

    @classmethod
    def teardown_class(cls):
        with cls.app.app_context():
            db.session.close()
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main(verbosity=2)