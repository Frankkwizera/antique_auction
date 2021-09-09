__author__ = "Frank Kwizera"

from src.storage.database_provider import db_provider
from sqlalchemy.orm.session import sessionmaker as Session
from flask_sqlalchemy import SQLAlchemy
from src.storage.database_tables import User, Item, Bid, AutoBid
from werkzeug.security import generate_password_hash
from src.shared.constants import GeneralConstants
from flask import Flask
from typing import List
import datetime

db: SQLAlchemy = db_provider.db

class DatabaseClient:
    def __init__(self, session: Session = None, app: Flask = None,
                 use_new_session: bool = False):
        if use_new_session:
            self.session = db_provider.get_new_session()
        elif session is not None:
            self.session = session
        elif db.session is not None:
            self.session = db.session

    def add_to_database(self, records: List[db.Model]):
        """
        Add database records to the database and commit the changes
        """
        for record in records:
            self.session.add(record)
        self.session.commit()

class UserDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        DatabaseClient.__init__(self, *args, **kwargs)
    
    def create_and_save_new_user(
            self, user_names: str = None, user_email: str = None, 
            user_password: str = None) -> User:
        user_password_hash: str = generate_password_hash(user_password, method=GeneralConstants.PASSWORD_HASHING_METHOD)
        new_user: User = User(user_names=user_names, user_email=user_email, user_password_hash=user_password_hash)
        self.add_to_database(records=[new_user])
        return new_user
    
    def check_if_user_exists(self, user_uuid: str) -> bool:
        """
        Checks if an user exists.
        Inputs:
            - user_uuid: UUID representing a target user.
        Returns:
            - True if item user, otherwise False.
        """
        return self.session.query(User).filter(User.user_uuid == user_uuid).scalar() is not None


class ItemDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        DatabaseClient.__init__(self, *args, **kwargs)
    
    def create_and_save_new_item(
            self, item_name: str = None, item_description: str = None, item_base_price_in_usd: int = None,
            item_owner_uuid: str = None, bid_expiration_timestamp: datetime.datetime = None) -> Item:
        new_item: Item = Item(
            item_name=item_name, item_description=item_description, 
            item_base_price_in_usd=item_base_price_in_usd, item_owner_uuid=item_owner_uuid, 
            bid_expiration_timestamp=bid_expiration_timestamp)
        
        self.add_to_database(records=[new_item])
        return new_item
    
    def retrieve_all_items(self) -> List[Item]:
        """
        Retrieves all stored auction items.
        Returns:
            - List of all items.
        """
        return self.session.query(Item).all()

    def retrieve_item_by_item_uuid(self, item_uuid: str) -> Item:
        """
        Retrieve item by item uuid.
        Inputs:
            - item_uuid: UUID representing the target item.
        Returns:
            - Item record.
        """
        return self.session.query(Item).filter(Item.item_uuid == item_uuid).one_or_none()
    
    def check_if_item_exists(self, item_uuid: str) -> bool:
        """
        Checks if an item exists.
        Inputs:
            - item_uuid: UUID representing a target item.
        Returns:
            - True if item exists, otherwise False.
        """
        return self.session.query(Item).filter(Item.item_uuid == item_uuid).scalar() is not None


class BidDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        DatabaseClient.__init__(self, *args, **kwargs)
    
    def create_item_bid(
            self, bid_price_in_usd: int, bid_item_uuid: str,
            bidder_uuid: str) -> Bid:
        new_bid: Bid = Bid(bid_price_in_usd=bid_price_in_usd, bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
        self.add_to_database(records=[new_bid])
        return new_bid

    def retrieve_item_bids(self, item_uuid: str) -> List[Bid]:
        return self.session.query(Bid).filter(Bid.bid_item_uuid == item_uuid).all()
    
    def retrieve_item_most_recent_bid(self, item_uuid: str) -> List[Bid]:
        """
        Retrieves item most recent bid.
        Returns:
            - Item most recent bid record.
        """
        return self.session.query(Bid).filter(Bid.bid_item_uuid == item_uuid).order_by(Bid.bid_id.desc()).first()


class AutoBidDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        DatabaseClient.__init__(self, *args, **kwargs)
    
    def register_auto_bid(self, bid_item_uuid: str, bidder_uuid: str) -> AutoBid:
        auto_bid: AutoBid = AutoBid(bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
        self.add_to_database(records=[auto_bid])
        return auto_bid
    
    def check_if_user_auto_bid_exists(self, bid_item_uuid: str, bidder_uuid: str) -> bool:
        return self.session.query(AutoBid).filter(
            AutoBid.bid_item_uuid == bid_item_uuid, 
            AutoBid.bidder_uuid == bidder_uuid).scalar() is not None