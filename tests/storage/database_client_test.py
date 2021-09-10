__author__ = "Frank Kwizera"

from src.storage.database_client import UserDatabaseClient, BidDatabaseClient
from src.storage.database_client import ItemDatabaseClient
from src.storage.database_tables import User, Bid, Item
from src.storage.database_provider import db_provider
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from src.get_app import get_app
import unittest
import uuid
import datetime

db: SQLAlchemy = db_provider.db


class DatabaseClientTest:
    def __init__(self):
        self.user_database_client: UserDatabaseClient = UserDatabaseClient()
        self.bid_database_client: BidDatabaseClient = BidDatabaseClient()
        self.item_database_client: ItemDatabaseClient = ItemDatabaseClient()
    

class UserDatabaseClientTest(unittest.TestCase, DatabaseClientTest):
    def setUp(self):
        self.app: Flask = get_app()
        self.app.app_context().push()

        DatabaseClientTest.__init__(self)
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_create_and_save_new_user(self):
        user_details: Dict[str, str] = {
            'user_names': 'Frank Kwizera Seller',
            'user_email': 'frank@gmail.com',
            'user_password': '1234567'
        }

        new_user: User = self.user_database_client.create_and_save_new_user(**user_details)
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.user_names, user_details['user_names'])
        self.assertEqual(new_user.user_email, user_details['user_email'])
    
    def test_check_if_user_exists(self):
        user_details: Dict[str, str] = {
            'user_names': 'Frank Kwizera Seller',
            'user_email': 'frank@gmail.com',
            'user_password': '1234567'
        }

        new_user: User = self.user_database_client.create_and_save_new_user(**user_details)
        user_exists: bool =  self.user_database_client.check_if_user_exists(user_uuid=new_user.user_uuid)
        self.assertTrue(user_exists)

        non_existing_user: bool =  self.user_database_client.check_if_user_exists(user_uuid='new_user.user_uuid')
        self.assertFalse(non_existing_user)

    def tearDown(self):
        with self.app.app_context():
            db.session.close()
            db.session.remove()
            db.drop_all()


class BidDatabaseClientTest(unittest.TestCase, DatabaseClientTest):
    def setUp(self):
        self.app: Flask = get_app()
        self.app.app_context().push()

        DatabaseClientTest.__init__(self)
        db.session.remove()
        db.drop_all()
        db.create_all()


        self.bid_1_details: Dict[str, str] = {
            'bid_price_in_usd': 250, 
            'bid_item_uuid': str(uuid.uuid4()),
            'bidder_uuid': str(uuid.uuid4())
        }
        self.bid_1: Bid = self.bid_database_client.create_item_bid(**self.bid_1_details)

        self.bid_2_details: Dict[str, str] = {
            'bid_price_in_usd': 251, 
            'bid_item_uuid': self.bid_1_details['bid_item_uuid'],
            'bidder_uuid': str(uuid.uuid4())
        }
        self.bid_2: Bid = self.bid_database_client.create_item_bid(**self.bid_2_details)

        self.bid_3_details: Dict[str, str] = {
            'bid_price_in_usd': 252, 
            'bid_item_uuid': self.bid_1_details['bid_item_uuid'],
            'bidder_uuid': str(uuid.uuid4())
        }
        self.bid_3 = self.bid_database_client.create_item_bid(**self.bid_3_details)

    def test_create_item_bid(self):
        self.assertIsInstance(self.bid_1, Bid)
        self.assertEqual(self.bid_1.bid_item_uuid, self.bid_1_details['bid_item_uuid'])
        self.assertEqual(self.bid_1.bid_price_in_usd, self.bid_1_details['bid_price_in_usd'])
        self.assertEqual(self.bid_1.bidder_uuid, self.bid_1_details['bidder_uuid'])

    def test_retrieve_item_bids(self):
        retrieved_bids: List[Bid] = \
            self.bid_database_client.retrieve_item_bids(
                item_uuid=self.bid_1_details['bid_item_uuid'])
        self.assertEqual(3, len(retrieved_bids))
        for bid in retrieved_bids:
            self.assertIsInstance(bid, Bid)
            self.assertEqual(bid.bid_item_uuid, self.bid_1_details['bid_item_uuid'])

    def test_retrieve_item_most_recent_bid(self):
        new_bid_details: Dict[str, str] = {
            'bid_price_in_usd': 255, 
            'bid_item_uuid': self.bid_1_details['bid_item_uuid'],
            'bidder_uuid': str(uuid.uuid4())
        }
        new_bid: Bid = self.bid_database_client.create_item_bid(**new_bid_details)
        most_recent_bid: Bid = \
            self.bid_database_client.retrieve_item_most_recent_bid(
                item_uuid=self.bid_1_details['bid_item_uuid'])
        self.assertEqual(new_bid.to_json_dict(), most_recent_bid.to_json_dict())

    def tearDown(self):
        with self.app.app_context():
            db.session.close()
            db.session.remove()
            db.drop_all()


class ItemDatabaseClientTest(unittest.TestCase, DatabaseClientTest):
    def setUp(self):
        self.app: Flask = get_app()
        self.app.app_context().push()

        DatabaseClientTest.__init__(self)
        db.session.remove()
        db.drop_all()
        db.create_all()

        self.item_details: Dict[str, Union[str, int]] = {
            'item_name': 'Item 1', 
            'item_description': 'Item 1 description',
            'item_base_price_in_usd': 250,
            'item_owner_uuid': str(uuid.uuid4()),
            'bid_expiration_timestamp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }

        self.item: Item = self.item_database_client.create_and_save_new_item(**self.item_details)

    def test_create_and_save_new_item(self):
        self.assertIsInstance(self.item, Item)
        self.assertEqual(self.item.item_name, self.item_details['item_name'])
        self.assertEqual(self.item.item_description, self.item_details['item_description'])
        self.assertEqual(self.item.item_base_price_in_usd, self.item_details['item_base_price_in_usd'])
        self.assertEqual(self.item.item_owner_uuid, self.item_details['item_owner_uuid'])
        self.assertEqual(self.item.bid_expiration_timestamp, self.item_details['bid_expiration_timestamp'])

    def test_retrieve_all_items(self):
        all_items: List[Item] = self.item_database_client.retrieve_all_items()
        self.assertEqual(1, len(all_items))
        self.assertEqual(self.item.to_json_dict(), all_items[0].to_json_dict())

    def test_retrieve_item_by_item_uuid(self):
        retrieved_item: Item = \
            self.item_database_client.retrieve_item_by_item_uuid(item_uuid=str(uuid.uuid4()))
        self.assertIsNone(retrieved_item)

        retrieved_item: Item = \
            self.item_database_client.retrieve_item_by_item_uuid(item_uuid=self.item.item_uuid)
        self.assertIsInstance(retrieved_item, Item)
        self.assertEqual(retrieved_item, self.item)

    def tearDown(self):
        with self.app.app_context():
            db.session.close()
            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main(verbosity=2)