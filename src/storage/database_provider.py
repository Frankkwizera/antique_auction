__author__ = "Frank Kwizera"

from flask_sqlalchemy import SQLAlchemy
from copy import deepcopy
from sqlalchemy.orm import sessionmaker as Session
from sqlalchemy.orm import scoped_session

from typing import Dict, Any


class DatabaseProvider:
    """
    Provides database access to all modules of the project.
    """

    def __init__(self):
        # Load lazily: Do not initialize the datatabase unless it's requested.
        self.__db: SQLAlchemy = None

    def __getstate__(self):
        """
        Invoked before pickling the object such as when exiting the parent process to start a child process.
        Remove ``__db`` reference from the state
        See https://docs.python.org/3/library/pickle.html#object.__getstate__
        """
        state: Dict[str, Any] = deepcopy(self.__dict__)
        del state['__db']
        return state

    def __setstate__(self, state: Dict[str, Any]):
        """
        Invoked when unpickling object to restore its state, such as entering a child process.
        Set ``__db`` reference to ``None`` so that next invoker can initialize it again
        See https://docs.python.org/3/library/pickle.html#object.__setstate__
        """
        self.__dict__.update(state)
        self.__dict__['__db'] = None

    @property
    def db(self):
        if self.__db is None:
            self.__db = SQLAlchemy()
        return self.__db

    @db.setter
    def db(self, value):
        raise PermissionError("Db attribute cannot be changed when it's set.")

    def close_and_remove_context_db_connection(self):
        if self.__db:
            self.db.get_engine().dispose()
            self.db.session.close_all()
            self.__db = None

    def get_new_session(self):
        from src.server.get_app import get_app
        session_factory: Session = Session(bind=self.db.get_engine(app=get_app()))
        return scoped_session(session_factory)

    def recover_context_db_connection(self):
        if self.__db is None:
            self.__db = SQLAlchemy()


# Provide this copy to the entire module. Clients can still create instances of DataBaseProvider.
db_provider = DatabaseProvider()