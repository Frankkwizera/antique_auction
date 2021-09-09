__author__ = "Frank Kwizera"

from src.shared.constants import GeneralConstants
from src.storage.database_provider import db_provider
from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid


db: SQLAlchemy = db_provider.db


class User(db.Model):
    user_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_uuid = db.Column(db.String(GeneralConstants.UUID_MAX_LENGTH), unique=True, index=True, nullable=False)
    user_names = db.Column(db.String(GeneralConstants.NAME_MAX_LENGTH), nullable=False)
    user_email = db.Column(db.String(GeneralConstants.EMAIL_MAX_LENGTH), unique=True, nullable=False)
    user_password_hash = db.Column(db.String(GeneralConstants.PASSWORD_HASH_MAX_LENGTH), nullable=False)

    def __init__(self, user_names: str = None, user_email: str = None,
                 user_password_hash: str = None):

        self.user_uuid = str(uuid.uuid4())
        self.user_names = user_names
        self.user_email = user_email
        self.user_password_hash = user_password_hash

    def __repr__(self):
        return "<User: {} {}>".format(self.user_names, self.user_email)

    def to_json_dict(self):
        """
        Returns serializable format.
        """
        return {
            'user_id': self.user_id,
            'user_uuid': self.user_uuid,
            'user_names': self.user_names,
            'user_email': self.user_email
        }

class Item(db.Model):
    item_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    item_uuid = db.Column(db.String(GeneralConstants.UUID_MAX_LENGTH), unique=True, index=True, nullable=False)
    item_name = db.Column(db.String(GeneralConstants.NAME_MAX_LENGTH), nullable=False)
    item_description = db.Column(db.String(GeneralConstants.DESCRIPTION_MAX_LENGTH), nullable=False)
    item_base_price_in_usd = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"))
    item_owner_uuid = db.Column(
        db.String(GeneralConstants.UUID_MAX_LENGTH), 
        db.ForeignKey('user.user_uuid', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    bid_expiration_timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, item_name: str = None, item_description: str = None, item_base_price_in_usd: int = None,
                 item_owner_uuid: str = None, bid_expiration_timestamp: datetime.datetime = None):

        self.item_uuid = str(uuid.uuid4())
        self.item_name = item_name
        self.item_description = item_description
        self.item_base_price_in_usd = item_base_price_in_usd
        self.item_owner_uuid = item_owner_uuid
        self.bid_expiration_timestamp = bid_expiration_timestamp
    
    def __repr__(self):
        return "<Item: {} {}>".format(self.item_name, self.item_base_price_in_usd)

    def to_json_dict(self):
        """
        Returns serializable format.
        """
        return {
            'item_id': self.item_id,
            'item_uuid': self.item_uuid,
            'item_name': self.item_name,
            'item_description': self.item_description,
            'item_base_price_in_usd': self.item_base_price_in_usd,
            'item_owner_uuid': self.item_owner_uuid,
            'bid_expiration_timestamp': self.bid_expiration_timestamp
        }

class Bid(db.Model):
    bid_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    bid_uuid = db.Column(db.String(GeneralConstants.UUID_MAX_LENGTH), unique=True, index=True, nullable=False)
    bid_price_in_usd = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"))
    bid_item_uuid = db.Column(
        db.String(GeneralConstants.UUID_MAX_LENGTH), 
        db.ForeignKey('item.item_uuid', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    bidder_uuid = db.Column(
        db.String(GeneralConstants.UUID_MAX_LENGTH), 
        db.ForeignKey('user.user_uuid', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    
    def __init__(self, bid_price_in_usd: int, bid_item_uuid: str, bidder_uuid: str):
        self.bid_uuid = str(uuid.uuid4())
        self.bid_price_in_usd = bid_price_in_usd
        self.bid_item_uuid = bid_item_uuid
        self.bidder_uuid = bidder_uuid

    def __repr__(self):
        return "<Bid: {} {}>".format(self.bid_uuid, self.bid_price_in_usd)

    def to_json_dict(self):
        """
        Returns serializable format.
        """
        return {
            'bid_id': self.bid_id,
            'bid_uuid': self.bid_uuid,
            'bid_price_in_usd': self.bid_price_in_usd,
            'bid_item_uuid': self.bid_item_uuid,
            'bidder_uuid': self.bidder_uuid
        }


class AutoBid(db.Model):
    auto_bid_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    auto_bid_uuid = db.Column(db.String(GeneralConstants.UUID_MAX_LENGTH), unique=True, index=True, nullable=False)
    bid_item_uuid = db.Column(
        db.String(GeneralConstants.UUID_MAX_LENGTH), 
        db.ForeignKey('item.item_uuid', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    bidder_uuid = db.Column(
        db.String(GeneralConstants.UUID_MAX_LENGTH), 
        db.ForeignKey('user.user_uuid', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('bid_item_uuid', 'bidder_uuid'), )
    
    def __init__(self, bid_item_uuid: str, bidder_uuid: str):
        self.auto_bid_uuid = str(uuid.uuid4())
        self.bid_item_uuid = bid_item_uuid
        self.bidder_uuid = bidder_uuid

    def __repr__(self):
        return "<AutoBid: {} {}>".format(self.auto_bid_uuid, self.bid_item_uuid)

    def to_json_dict(self):
        """
        Returns serializable format.
        """
        return {
            'auto_bid_id': self.auto_bid_id,
            'auto_bid_uuid': self.auto_bid_uuid,
            'bid_item_uuid': self.bid_item_uuid,
            'bidder_uuid': self.bidder_uuid
        }
