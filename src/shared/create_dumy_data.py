__author__ = "Frank Kwizera"

from src.storage.database_client import UserDatabaseClient, ItemDatabaseClient, BidDatabaseClient
from src.storage.database_tables import User, Item, Bid
from src.storage.database_provider import db_provider
from src.get_app import get_app
from typing import Dict, List, Union
from flask import Flask
import datetime
from flask_sqlalchemy import SQLAlchemy
import logging


db: SQLAlchemy = db_provider.db


class DummyDataCreator:
    def __init__(self):
        self.app: Flask = get_app()
        self.app.logger.setLevel(logging.INFO)
        self.app.app_context().push()
        db.drop_all()
        db.create_all()

        # Initialize database clients.
        self.user_database_client: UserDatabaseClient = UserDatabaseClient()
        self.item_database_client: ItemDatabaseClient = ItemDatabaseClient()
        self.bid_database_client: BidDatabaseClient = BidDatabaseClient()

        # Dummy user details.
        self.user_details: List[Dict[str, str]] = [
            {
                'user_names': 'Frank Kwizera Seller',
                'user_email': 'frank@gmail.com',
                'user_password': '1234567'
            },
            {
                'user_names': 'Frank Kwizera Buyer',
                'user_email': 'frank2@gmail.com',
                'user_password': '1234567'
            }
        ]

    def intiate_dummy_data_creation(self):
        """
        Initiates the process of creating dummy data such as user records and item records.
        """

        # Create users.
        created_users: List[Dict[str, str]] = []
        for user_info in self.user_details:
            created_users.append(self.create_user(user_info=user_info))

        # Create items.
        self.auction_items: List[Dict[str, Union[str, int]]]= [
            {
                'item_name': 'Item 1', 
                'item_description': 'Item 1 description',
                'item_base_price_in_usd': 200,
                'item_owner_uuid': created_users[0]['user_uuid'],
                'bid_expiration_timestamp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            {
                'item_name': 'Item 2', 
                'item_description': 'Item 2 description',
                'item_base_price_in_usd': 250,
                'item_owner_uuid': created_users[0]['user_uuid'],
                'bid_expiration_timestamp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }
        ]

        for auction_item in self.auction_items:
            item_dict: Dict[str, str] = self.create_item(auction_item_dict=auction_item)
            # Create one dummy bid.
            bid_dict: Dict[str, str] = {
                'bid_price_in_usd': 250, 
                'bid_item_uuid': item_dict['item_uuid'],
                'bidder_uuid': created_users[1]['user_uuid']
            }

            self.create_bid(bid_dict=bid_dict)

    def create_user(self, user_info: Dict[str, str]) -> Dict[str, str]:
        """
        Creates a dummy user record.
        Inputs:
            - user_info: Dictionary representing user information
        Returns:
            - Json dict of the created user.
        """
        dumy_user: User = self.user_database_client.create_and_save_new_user(**user_info)
        self.app.logger.info(f'User created with the following details: Names: {dumy_user.user_names} Email: {dumy_user.user_email} UUID: {dumy_user.user_uuid}')
        return dumy_user.to_json_dict()

    def create_item(self, auction_item_dict: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
        """
        Creates a dummy item record.
        Inputs:
            - auction_item_dict: Dictionary representing auction item.
        Returns:
            - Json dict of the created item.
        """
        dummy_item: Item = self.item_database_client.create_and_save_new_item(**auction_item_dict)
        self.app.logger.info(f'Item created with the following details: Item Name: {dummy_item.item_name} Base Price: {dummy_item.item_base_price_in_usd}')
        return dummy_item.to_json_dict()

    def create_bid(self, bid_dict: Dict[str, str]) -> Dict[str, str]:
        """
        Creates a dummy bid record.
        Inputs:
            - bid_dict: Dictionary representing bid details.
        Returns:
            - Json dict of the created bid.
        """
        dummy_bid: Bid = self.bid_database_client.create_item_bid(**bid_dict)
        self.app.logger.info(f'Bid created with the following details: Item UUID: {dummy_bid.bid_item_uuid} Bid Price: {dummy_bid.bid_price_in_usd}')
        return dummy_bid.to_json_dict()


if __name__ == "__main__":
    dummy_data_creator: DummyDataCreator = DummyDataCreator()
    dummy_data_creator.intiate_dummy_data_creation()