__author__ = "Frank Kwizera"

from flask import Flask
from src.server.user_management_server import UserManagementServer
from src.server.item_management_server import ItemManagementServer
from src.server.bid_management import BidManagementServer
from src.get_app import get_app
from src.storage.database_provider import db_provider

db = db_provider.db

class AuctionServerRunner:
    def __init__(self):
        self.debug: bool = True
        self.app: Flask = get_app()

        # Initialize database tables.
        with self.app.app_context():
            db.create_all()

    def attach_micro_servers(self):
        """
        Initiates different micro servers.
        """
        self.user_management_server: UserManagementServer = UserManagementServer()
        self.item_management_server: ItemManagementServer = ItemManagementServer()
        self.bid_management_server: BidManagementServer = BidManagementServer()

    def start(self, port: int = None):
        """
        Initiates the flask server.
        Inputs:
            - port: Desired port number.
        """
        self.app.run(host="0.0.0.0", debug=self.debug, port=port)


if __name__ == "__main__":
    auction_server_runner: AuctionServerRunner = AuctionServerRunner()
    auction_server_runner.attach_micro_servers()
    auction_server_runner.start(port=5050)