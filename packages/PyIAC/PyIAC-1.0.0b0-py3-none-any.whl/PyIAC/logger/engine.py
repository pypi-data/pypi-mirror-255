# -*- coding: utf-8 -*-
"""PyIAC/logger/engine.py

This module implements a singleton layer above the DataLogger class,
in a thread-safe mode.
"""

import threading
from .datalogger import DataLogger
from .._singleton import Singleton


class DataLoggerEngine(Singleton):
    r"""
    Data logger Engine class for Tag thread-safe database logging.

    """

    def __init__(self):

        super(DataLoggerEngine, self).__init__()

        self._logger = DataLogger()
        self._logging_tags = list()

        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response = None

        self._response_lock.acquire()

    def set_db(self, db):
        r"""
        Initialize a new DB Object SQLite - Postgres - MySQL

        **Parameters**

        * **db** (db object): Sqlite - Postgres or MySql db object

        **Returns** `None`
        """
        self._logger.set_db(db)

    def get_db(self):
        r"""
        Returns a DB object
        """
        return self._logger.get_db()

    def create_tables(self, tables):
        r"""
        Create default PyIAC database tables

        ['TagTrend', 'TagValue']

        **Parameters**

        * **tables** (list) list of database model

        **Returns** `None`
        """
        self._logger.create_tables(tables)

    def drop_tables(self, tables:list):
        r"""
        Drop tables if exist in database

        **Parameters**

        * **tables** (list): List of database model you want yo drop
        """
        self._logger.drop_tables(tables)

    def set_tag(
        self, 
        tag, 
        unit:str, 
        data_type:str, 
        description:str,
        display_name:str="", 
        min_value:float=None, 
        max_value:float=None, 
        tcp_source_address:str=None, 
        node_namespace:str=None):
        r"""
        Define tag names you want log in database, these tags must be defined in CVTEngine

        **Parameters**

        * **tag** (str): Tag name defined in CVTEngine
        * **period** (float): Sampling time to log tag on database

        **Returns** `None`
        """
        self._logger.set_tag(
            tag=tag,
            unit=unit,
            data_type=data_type,
            description=description,
            display_name=display_name,
            min_value=min_value,
            max_value=max_value,
            tcp_source_address=tcp_source_address,
            node_namespace=node_namespace
        )

    def write_tag(self, tag, value):
        r"""
        Writes value to tag into database on a thread-safe mechanism

        **Parameters**

        * **tag** (str): Tag name in database
        * **value** (float): Value to write in tag
        """
        _query = dict()
        _query["action"] = "write_tag"

        _query["parameters"] = dict()
        _query["parameters"]["tag"] = tag
        _query["parameters"]["value"] = value

        self.request(_query)
        result = self.response()

        return result

    def write_tags(self, tags:list):
        r"""
        Writes value to tag into database on a thread-safe mechanism

        **Parameters**

        * **tag** (str): Tag name in database
        * **value** (float): Value to write in tag
        """
        _query = dict()
        _query["action"] = "write_tags"

        _query["parameters"] = dict()
        _query["parameters"]["tags"] = tags

        self.request(_query)
        result = self.response()

        return result

    def read_tag(self, tag):
        r"""
        Read tag value from database on a thread-safe mechanism

        **Parameters**

        * **tag** (str): Tag name in database

        **Returns**

        * **value** (float): Tag value requested
        """
        _query = dict()
        _query["action"] = "read_tag"

        _query["parameters"] = dict()
        _query["parameters"]["tag"] = tag

        self.request(_query)
        result = self.response()

        if result["result"]:
            
            return result["response"]

    def request(self, _query):
        r"""
        Documentation here
        """
        self._request_lock.acquire()

        action = _query["action"]

        if action == "write_tag":

            try:
                parameters = _query["parameters"]

                tag = parameters["tag"]
                value = parameters["value"]

                self._logger.write_tag(tag, value)

                self._response = {
                    "result": True
                }
            except Exception as e:
                self._response = {
                    "result": False
                }

        elif action == "write_tags":

            try:
                parameters = _query["parameters"]

                tags = parameters["tags"]

                self._logger.write_tags(tags)

                self._response = {
                    "result": True
                }
            except Exception as e:
                self._response = {
                    "result": False
                }
        
        elif action == "read_tag":

            try:

                parameters = _query["parameters"]

                tag = parameters["tag"]

                result = self._logger.read_tag(tag)
                
                self._response = {
                    "result": True,
                    "response": result
                }
            except Exception as e:
                self._response = {
                    "result": False,
                    "response": None
                }

        self._response_lock.release()

    def response(self):
        r"""
        Documentation here
        """
        self._response_lock.acquire()

        result = self._response

        self._request_lock.release()

        return result

    def __getstate__(self):

        self._response_lock.release()
        state = self.__dict__.copy()
        del state['_request_lock']
        del state['_response_lock']
        return state

    def __setstate__(self, state):
        
        self.__dict__.update(state)
        self._request_lock = threading.Lock()
        self._response_lock = threading.Lock()

        self._response_lock.acquire()
