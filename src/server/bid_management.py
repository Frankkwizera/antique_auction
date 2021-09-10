__author__ = "Frank Kwizera"

from src.server.server_helper import ServerHelper
from src.shared.server_routes import BidManagementServerRoutes  
from src.storage.database_client import BidDatabaseClient, UserDatabaseClient
from src.storage.database_client import ItemDatabaseClient, AutoBidDatabaseClient
from src.storage.database_tables import Bid, AutoBid, UserAutoBid
from flask import jsonify, Flask, request, wrappers
from src.get_app import get_app
from flask_api import status
import datetime


class BidManagementServer:
    def __init__(self):
        self.app: Flask = get_app()
        self.map_endpoints(app=self.app)

        # Initiate database clients.
        self.bid_database_client: BidDatabaseClient = BidDatabaseClient()
        self.user_database_client: UserDatabaseClient = UserDatabaseClient()
        self.item_database_client: ItemDatabaseClient = ItemDatabaseClient()
        self.auto_bid_database_client: AutoBidDatabaseClient = AutoBidDatabaseClient()

    def map_endpoints(self, app: Flask):
        """
        Maps all bid management server routes to the corresponding methods.
        """
        app.add_url_rule(
            BidManagementServerRoutes.CREATE_BID, endpoint="submit_a_bid",
            view_func=self.submit_a_bid, methods=['POST'])
        
        app.add_url_rule(
            BidManagementServerRoutes.REGISTER_AUTO_BID, endpoint="register_auto_bid",
            view_func=self.register_auto_bid, methods=['POST'])

        app.add_url_rule(
            BidManagementServerRoutes.REGISTER_USER_AUTO_CONFI_BID, endpoint="register_user_auto_bid_configuration",
            view_func=self.register_user_auto_bid_configuration, methods=['POST'])
    
    def register_user_auto_bid_configuration(self) -> wrappers.Response:
        """
        Registers user auto bid configuration.
        Returns:
            - Http response to the client.
        """
        request_data: Dict[str, str] = request.get_json()
        max_bid_amount_in_usd: str = request_data.get('max_bid_amount_in_usd')
        bidder_uuid: str = request_data.get('bidder_uuid')

        # Check if auto bid configuration is registered.
        if self.auto_bid_database_client.check_if_user_auto_bidder_config_exists(bidder_uuid=bidder_uuid):
            return ServerHelper.create_http_response(
                message='User auto bid configuration exists.', 
                status=status.HTTP_400_BAD_REQUEST)

        user_auto_bid: UserAutoBid = \
            self.auto_bid_database_client.register_user_auto_bid_config(
                bidder_uuid=bidder_uuid, max_bid_amount_in_usd=max_bid_amount_in_usd)
        return jsonify(user_auto_bid.to_json_dict())

    def register_auto_bid(self) -> wrappers.Response:
        """
        Registers auto bid on an item.
        Returns:
            - Http response indicating the success or failure of item auto bid registration.
        """
        request_data: Dict[str, str] = request.get_json()
        bid_item_uuid: str = request_data.get('bid_item_uuid')
        bidder_uuid: str = request_data.get('bidder_uuid')

        # Check if user exists.
        if not self.user_database_client.check_if_user_exists(user_uuid=bidder_uuid):
            return ServerHelper.create_item_not_found_message(message=f'User with uuid {bidder_uuid} does not exists.')

        # Check if item exists.
        if not self.item_database_client.check_if_item_exists(item_uuid=bid_item_uuid):
            return ServerHelper.create_item_not_found_message(message=f'Item with uuid {bid_item_uuid} does not exists.')
        
        # Check if auto bid already exists.
        if self.auto_bid_database_client.check_if_user_auto_bid_exists(
                bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid):
            return ServerHelper.create_http_response(
                message='Auto bid on this item already exists.', 
                status=status.HTTP_400_BAD_REQUEST)
        
        new_auto_bid: AutoBid = \
            self.auto_bid_database_client.register_auto_bid(
                bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
        return jsonify(new_auto_bid.to_json_dict())

    def submit_a_bid(self) -> wrappers.Response:
        """
        Submits the item bid.
        Returns:
            - Http response indicating the success or failure of item bid.
        """
        request_data: Dict[str, str] = request.get_json()
        bid_price_in_usd: int = int(request_data.get('bid_price_in_usd'))
        bid_item_uuid: str = request_data.get('bid_item_uuid')
        bidder_uuid: str = request_data.get('bidder_uuid')

        # Check if user exists.
        if not self.user_database_client.check_if_user_exists(user_uuid=bidder_uuid):
            return ServerHelper.create_item_not_found_message(message=f'User with uuid {bid_item_uuid} does not exists.')

        # Check if item exists.
        if not self.item_database_client.check_if_item_exists(item_uuid=bid_item_uuid):
            return ServerHelper.create_item_not_found_message(message=f'Item with uuid {bid_item_uuid} does not exists.')

        # Check if the bid is greater than the most recent bid.
        item_most_recent_bid: Bid = self.bid_database_client.retrieve_item_most_recent_bid(item_uuid=bid_item_uuid)
        if item_most_recent_bid and item_most_recent_bid.bid_price_in_usd >= bid_price_in_usd:
            return ServerHelper.create_http_response(
                message=f'Bid price should be higher than {item_most_recent_bid.bid_price_in_usd}', status=status.HTTP_400_BAD_REQUEST)

        new_bid_response: wrappers.Response = \
            self.place_a_bid(bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid, bid_price_in_usd=bid_price_in_usd)
        return new_bid_response
    
    def place_a_bid(self, bid_item_uuid: str, bidder_uuid: str, bid_price_in_usd: int) -> wrappers.Response:
        """
        Places an item bid with a given amount.
        Returns:
            - Http response indicating the success or failure of item bid placement.
        """
        # Check the bid close date.
        item_close_date: datetime.datetime = \
            self.item_database_client.retrieve_item_close_date(item_uuid=bid_item_uuid)
        if datetime.datetime.utcnow() > item_close_date:
            return ServerHelper.create_http_response(
                message='Bid is closed now', status=status.HTTP_400_BAD_REQUEST)

        new_bid: Bid = self.bid_database_client.create_item_bid(
            bid_price_in_usd=bid_price_in_usd, bid_item_uuid=bid_item_uuid, bidder_uuid=bidder_uuid)
       
        registered_item_auto_bidders_uuids_with_enough_funds: List[str] = \
            self.auto_bid_database_client.retrieve_item_auto_bidders_uuids_with_enough_funds(
                item_uuid=bid_item_uuid, highest_bider_uuid=bidder_uuid, current_highest_bid=new_bid.bid_price_in_usd)
        
        for auto_bidder_uuid in registered_item_auto_bidders_uuids_with_enough_funds:
            self.place_a_bid(
                bid_item_uuid=bid_item_uuid, bidder_uuid=auto_bidder_uuid, 
                bid_price_in_usd=bid_price_in_usd + 1)
        
        return jsonify(new_bid.to_json_dict())