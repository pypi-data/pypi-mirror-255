import logging

from .base import BaseDBConnection
import redshift_connector
from bluescope.logger import setup_logger
import time

logger = setup_logger(__name__)


class RedshiftServerlessConnection(BaseDBConnection):
    stats_query = ("SELECT query_id, execution_time FROM SYS_QUERY_HISTORY WHERE query_text like '{}' "
                   "AND start_time>TO_TIMESTAMP('{}', 'YYYY-MM-DD HH24:MI:SS.FF') "
                   "AND user_id = {} "
                   "ORDER BY start_time DESC LIMIT 1")
    connection = None

    def __init__(self, host: str, port: int, db: str, user: str, password: str):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.connect()

        with self.connection.cursor() as cursor:
            cursor.execute('SELECT user, current_user_id;')
            self.user_name, self.user_id = cursor.fetchone()
            logger.info(f"Connected to Redshift as user: {self.user_name} (id: {self.user_id})")

    def close(self):
        if self.connection:
            self.connection.close()
    # executes and runs get_stats
    def connect(self):
        if self.connection:
            self.connection.close()
        self.connection = redshift_connector.connect(
            host=self.host,
            port=self.port,
            database=self.db,
            user=self.user,
            password=self.password,
            is_serverless=True,
        )
        with self.connection.cursor() as cursor:
            cursor.execute('SET enable_result_cache_for_session TO off;')

    def execute(self, query: str, params: dict):
        self.connect()
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
        return cursor.rowcount

    def get_stats(self, query: str, datetime: str, params: dict = {}):
        """
        Get the query id and execution time for the given query
        :param user_id:
        :param query: str
        :param datetime: str in the format 'YYYY-MM-DD HH24:MI:SS.FF'
        :param params: dict
        :return: query_id, execution_tiem
        """
        self.connect()
        with self.connection.cursor() as cursor:
            query = self.stats_query.format(query, datetime, self.user_id)
            logger.debug('Executing query: ' + query)
            time.sleep(5)
            cursor.execute(query, params)
            query_id, execution_time = cursor.fetchall()[0]
        return query_id, execution_time
