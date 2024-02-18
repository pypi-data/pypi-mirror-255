# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

import pandas
from pydruid import db
from igrafx_mining_sdk.api_connector import APIConnector


class Datasource:
    """A Druid table that can be requested by the user"""
    def __init__(self, name: str, dstype: str, host: str, port: str, api_connector: APIConnector):
        """Initialise a datasource

        :param name: the name of the datasource
        :param dstype: the type of the datasource
        :param host: the host of the datasource
        :param port: the port number of the datasource
        :param api_connector: an APIConnector object that can be used to send requests to the datasource
        """

        self.name = name
        self.type = dstype
        self.host = host
        self.port = port
        self.api_connector = api_connector
        self._connection = None
        self._cursor = None
        self._columns = None

    def load_dataframe(self, load_limit=None):
        """Converts an SQL request to a dataframe

        :param load_limit: Maximum number of rows to load
        """
        sqlreq = f'SELECT * FROM "{self.name}"'
        if load_limit is not None:
            sqlreq += f'LIMIT {load_limit}'
        return self.request(sqlreq)

    def request(self, sqlreq):
        """Sends an SQL request to the datasource and returns the results as a pandas Dataframe

        :param sqlreq: the SQL request to execute
        """
        self.cursor.execute(sqlreq)
        rows = self.cursor.fetchall()
        cols = [i[0] for i in self.cursor.description]
        return pandas.DataFrame(rows, columns=cols)

    @property
    def columns(self):
        """Returns the columns of the datasource"""
        if self._columns is None:
            res = self.request(
                f"SELECT COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME ="
                f" '{self.name}' ORDER BY 2")
            self._columns = res["COLUMN_NAME"].to_list()
        return self._columns

    @property
    def connection(self):
        """Returns the Pydruid connection to the datasource, after initializing it, if need be"""
        if self._connection is None:
            self._connection = db.connect(self.host, self.port, path="/druid/v2/sql",
                                          user=self.api_connector.wg_id,
                                          password=self.api_connector.wg_key)
        return self._connection

    @property
    def cursor(self):
        """Returns the Pydruid cursor on the datasource, after initializing it if it doesn't exist"""
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    def close(self):
        """Closes the connection and the cursor if necessary"""
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None
        if self._connection is not None:
            self._connection.close()
            self._connection = None
