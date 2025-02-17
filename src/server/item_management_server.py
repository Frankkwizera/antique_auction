__author__ = "Frank Kwizera"

from src.shared.server_routes import ItemManagementServerRoutes
from src.storage.database_client import ItemDatabaseClient, BidDatabaseClient, AutoBidDatabaseClient
from src.storage.database_tables import Item, Bid
from src.server.server_helper import ServerHelper
from flask import jsonify, Flask, wrappers
from src.get_app import get_app
from typing import List, Dict, Union


class ItemManagementServer:
    def __init__(self):
        self.app: Flask = get_app()
        self.map_endpoints(app=self.app)

        # Initiate database clients.
        self.item_database_client: ItemDatabaseClient = ItemDatabaseClient()
        self.bid_database_client: BidDatabaseClient = BidDatabaseClient()
        self.auto_bid_database_client: AutoBidDatabaseClient = AutoBidDatabaseClient()

    def map_endpoints(self, app: Flask):
        """
        Maps all item management server routes to the corresponding methods.
        """
        app.add_url_rule(ItemManagementServerRoutes.RETRIEVE_ALL_ITEMS, endpoint="retrieve_all_items", view_func=self.retrieve_all_items, methods=['GET'])
        app.add_url_rule(ItemManagementServerRoutes.RETRIEVE_ITEM_DETAILS + '/<string:item_uuid>', endpoint="retrieve_item_details", view_func=self.retrieve_item_details, methods=['GET'])

    def retrieve_all_items(self) -> wrappers.Response:
        """
        Retrieves all stored items.
        Returns:
            - List of all items.
        """
        all_items: List[Item] = self.item_database_client.retrieve_all_items()
        return jsonify([item.to_json_dict() for item in all_items])
    
    def retrieve_item_details(self, item_uuid: str) -> wrappers.Response:
        """
        Retrieves single item details.
        Inputs:
            - item_uuid: UUID representing a target item record.
        Returns:
            - Item record json dictionary.
        """
        item: Item = self.item_database_client.retrieve_item_by_item_uuid(item_uuid=item_uuid)
        if not item:
            return ServerHelper.create_item_not_found_message()
        
        item_dict: Dict[str, Union[str, int]] = item.to_json_dict()
        # Retrieve registered bids.
        item_dict['item_bids'] = []
        item_bids: List[Bid] = self.bid_database_client.retrieve_item_bids(item_uuid=item.item_uuid)
        for item_bid in item_bids:
            item_dict['item_bids'].append(item_bid.to_json_dict())

        item_dict['item_auto_bidders'] = []
        item_auto_bidders: List[AutoBid] = \
            self.auto_bid_database_client.retrieve_item_auto_bidders(item_uuid=item.item_uuid)
        
        for item_auto_bidder in item_auto_bidders:
            item_dict['item_auto_bidders'].append(item_auto_bidder.to_json_dict())

        return jsonify(item_dict)