__author__ = "Frank Kwizera"

from src.storage.database_provider import db_provider
from sqlalchemy.orm.session import sessionmaker as Session
from flask_sqlalchemy import SQLAlchemy
from src.storage.database_tables import User, Item, Bid, AutoBid, UserAutoBid
from werkzeug.security import generate_password_hash, check_password_hash
from src.shared.constants import GeneralConstants
from flask import Flask
from typing import List, Tuple
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
        """
        Creates and save new user.
        Inputs:
            - user_names: User names.
            - user_email: User email.
            - user_password: User password.
        Returns:
            - Newly created user record.
        """
        user_password_hash: str = generate_password_hash(user_password, method=GeneralConstants.PASSWORD_HASHING_METHOD)
        new_user: User = User(user_names=user_names, user_email=user_email, user_password_hash=user_password_hash)
        self.add_to_database(records=[new_user])
        return new_user
    
    def authenticate_user(self, user_email: str, user_password: str) -> User:
        """
        Checks if submitted credentials matches the store user.
        Inputs:
            - user_email: User email.
            - user_password: User password.
        Returns:
            - User object if email and password matches, otherwise None.
        """
        user: User = self.session.query(User).filter(User.user_email == user_email).first()
        if user and check_password_hash(user.user_password_hash, user_password):
            return user
        return None
    
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
        """
        Creates and save an item record.
        Inputs:
            - item_name: Item name.
            - item_description: Item description.
            - item_base_price_in_usd: Base price in usd currency.
            - item_owner_uuid: Item owner uuid.
            - bid_expiration_timestamp: Item closing timestamp.
        Returns:
            - Newly created item record.
        """
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
    
    def retrieve_item_close_date(self, item_uuid: str) -> datetime.datetime:
        """
        Retrieves item close date.
        Inputs:
            - item_uuid: UUID representing the target item record.
        Returns:
            - Item closing date.
        """
        return self.session.query(Item.bid_expiration_timestamp).filter(
            Item.item_uuid == item_uuid).one_or_none()[0]


class BidDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        DatabaseClient.__init__(self, *args, **kwargs)
    
    def create_item_bid(self, bid_price_in_usd: int, 
                        bid_item_uuid: str, bidder_uuid: str) -> Bid:
        """ 
        Creates and saves item bid record.
        Inputs:
            - bid_price_in_usd: Suggested bid price.
            - bid_item_uuid: UUID representing the target uuid.
            - bidder_uuid: UUID representing the user.
        Returns:
            - Newly created bid record.
        """
        new_bid: Bid = Bid(bid_price_in_usd=bid_price_in_usd, bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
        self.add_to_database(records=[new_bid])
        return new_bid

    def retrieve_item_bids(self, item_uuid: str) -> List[Bid]:
        """
        Retrieves all item bids.
        Inputs:
            - item_uuid: UUID representing the item.
        Returns:
            - List of registered bids.
        """
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
    
    def register_user_auto_bid_config(
            self, bidder_uuid: str, max_bid_amount_in_usd: int):
        """
        Registers user auto bidding configuration.
        Inputs:
            - bidder_uuid: UUID representing the user.
            - max_bid_amount_in_usd: User max bid amount.
        Returns:
            - Newly created user auto bid configuration.
        """
        user_auto_bid: UserAutoBid = \
            UserAutoBid(bidder_uuid=bidder_uuid, max_bid_amount_in_usd=max_bid_amount_in_usd)
        self.add_to_database(records=[user_auto_bid])
        return user_auto_bid
    
    def check_if_user_auto_bidder_config_exists(self, bidder_uuid: str) -> bool:
        return self.session.query(UserAutoBid).filter(
            UserAutoBid.bidder_uuid == bidder_uuid).scalar() is not None
    
    def register_auto_bid(self, bid_item_uuid: str, bidder_uuid: str) -> AutoBid:
        auto_bid: AutoBid = AutoBid(bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
        self.add_to_database(records=[auto_bid])
        return auto_bid
    
    def check_if_user_auto_bid_exists(self, bid_item_uuid: str, bidder_uuid: str) -> bool:
        return self.session.query(AutoBid).filter(
            AutoBid.bid_item_uuid == bid_item_uuid, 
            AutoBid.bidder_uuid == bidder_uuid).scalar() is not None
    
    def retrieve_item_auto_bidders(self, item_uuid: str) -> List[AutoBid]:
        return self.session.query(AutoBid).filter(
            AutoBid.bid_item_uuid == item_uuid).all()
    
    def retrieve_item_auto_bidders_uuids_with_enough_funds(
            self, item_uuid: str, highest_bider_uuid: str, current_highest_bid: int) -> List[str]:
        """
        Retrieves auto bidders uuids with enough funds to place a bid.
        Inputs:
            - item_uuid: UUID representing a target item to place a bid on.
            - highest_bider_uuid: Current highest bidder uuid.
            - current_highest_bid: Current highest bid on the item.
        Returns:
            - List of auto bidders uuids.
        """
        item_auto_bidders_uuids: Tuple[str] = self.session.query(AutoBid.bidder_uuid).filter(
            AutoBid.bid_item_uuid == item_uuid,
            AutoBid.bidder_uuid != highest_bider_uuid).all()

        auto_bidders_with_enough_funds: List[str] = []
        for item_auto_bidder_uuid, in item_auto_bidders_uuids:
            auto_bidder_max_bid_amount_in_usd: int = \
                self.session.query(UserAutoBid.max_bid_amount_in_usd).filter(
                    UserAutoBid.bidder_uuid == item_auto_bidder_uuid).one_or_none()[0]
            number_of_bids_registered_by_user: int = self.session.query(AutoBid).filter(
                AutoBid.bidder_uuid == item_auto_bidder_uuid).count()
            average_bid_per_item: int = auto_bidder_max_bid_amount_in_usd / number_of_bids_registered_by_user

            if average_bid_per_item > current_highest_bid:
                auto_bidders_with_enough_funds.append(item_auto_bidder_uuid)

        return auto_bidders_with_enough_funds
        

        