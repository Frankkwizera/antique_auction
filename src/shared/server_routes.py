__author__ = "Frank Kwizera"


class UserManagementServerRoutes:
    CREATE_USER = "/create/user"
    USER_LOGIN = "/user/login"
    USER_LOGOUT = "/user/logout"


class ItemManagementServerRoutes:
    CREATE_ITEM = "/create/item"
    RETRIEVE_ALL_ITEMS = "/retrieve/all/items"
    RETRIEVE_ITEM_DETAILS = "/retrieve/item/details/"


class BidManagementServerRoutes:
    CREATE_BID = "/create/bid"
    REGISTER_AUTO_BID = "/register/auto/bid"
