__author__ = "Frank Kwizera"

from src.server.item_management_server import ItemManagementServer
from src.storage.database_client import ItemDatabaseClient
from src.storage.database_tables import Item
from src.storage.database_provider import db_provider
from src.shared.server_routes import ItemManagementServerRoutes
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


db: SQLAlchemy = db_provider.db


class ItemManagementServerTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.app: Flask = get_app()
        cls.client: FlaskClient = cls.app.test_client()
        cls.app.app_context().push()

        cls.itemserver = ItemManagementServer()

        db.session.remove()
        db.drop_all()
        db.create_all()

        # Initiate database clients.
        cls.item_database_client: ItemDatabaseClient = ItemDatabaseClient()
        cls.item_details: Dict[str, Union[str, int]] = {
            'item_name': 'Item 1', 
            'item_description': 'Item 1 description',
            'item_base_price_in_usd': 250,
            'item_owner_uuid': str(uuid.uuid4()),
            'bid_expiration_timestamp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        cls.item_record: Item = cls.item_database_client.create_and_save_new_item(**cls.item_details)

    def test_retrieve_all_items(self):
        all_items: Response = self.client.get(ItemManagementServerRoutes.RETRIEVE_ALL_ITEMS)
        self.assertEqual(all_items.status_code, 200)

        all_items_json_response: Dict[str, str] = json.loads(all_items.data)
        self.assertEqual(1, len(all_items_json_response))

    def test_retrieve_item_details(self):
        item_details_response: Response = \
            self.client.get(
                ItemManagementServerRoutes.RETRIEVE_ITEM_DETAILS + f'{self.item_record.item_uuid}')
        self.assertEqual(item_details_response.status_code, 200)

        item_details_json_response: Dict[str, str] = json.loads(item_details_response.data)
        self.assertEqual(item_details_json_response['item_uuid'], self.item_record.item_uuid)
        self.assertEqual(item_details_json_response['item_owner_uuid'], self.item_record.item_owner_uuid)
        self.assertEqual(item_details_json_response['item_base_price_in_usd'], self.item_record.item_base_price_in_usd)
    
    @classmethod
    def teardown_class(cls):
        with cls.app.app_context():
            db.session.close()
            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main(verbosity=2)