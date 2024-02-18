import datetime
from abc import ABC, abstractmethod
from statistics import stdev

from bluescope.db import REDSHIFT_SERVERLESS
from bluescope.db import get_connector
from bluescope.logger import setup_logger
from bluescope.statsutils import calculate_sample_size

logger = setup_logger(__name__)


class BaseProfiler(ABC):
    @abstractmethod
    def profile(self, query: str, count: int, params: dict):
        """Executes the query and returns the profile"""
        pass


class RedshiftServerlessProfiler(BaseProfiler):
    def __init__(self, **kwargs):
        """
        Initialize the RedshiftServerlessProfiler with a connection
        :param connection:
        """
        self.connection = get_connector(REDSHIFT_SERVERLESS)(host=kwargs['host'], port=kwargs['port'], db=kwargs['db'],
                                                             user=kwargs['user'], password=kwargs['password'])
        self.agree = kwargs['agree']

    def profile(self, query: str, params: dict = {}, p_value: float = 0.90, ):
        """
        Profile the query and return the profile results
        :param p_value:  The p-value to be used for the test
        :param query: SQL query to be profiled
        :param count: Number of times to run the query
        :param params: Any parameters to be passed to the query
        :return:
        """
        sample_size = calculate_sample_size(p=p_value)
        if not self.agree:
            answer = input(f"Sample size (amount of time query will be executed) is {sample_size}. "
                           f"Do you agree? (y/[N]): ")
            if answer.lower() != 'y':
                return None
        sample_size = 5
        logger.info(f"Profiling query: {query}")
        logger.info(f"Sample size: {sample_size}")
        stats = {'query_id': [], 'execution_time': []}
        for i in range(sample_size):
            # execute the query
            dt = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')
            logger.debug(f"Executing query {i + 1}/{sample_size} ({dt})")
            logger.debug(f"Query: {query}")
            rc = self.connection.execute(query, params)

            # obtain the query id and execution time
            logger.debug(f"Finished. Rows returned: {rc}")
            query_id, execution_time = self.connection.get_stats(query, dt, params)
            logger.debug(f"Query ID: {query_id}, Execution Time: {execution_time}")

            # store the results
            stats['query_id'].append(query_id)
            stats['execution_time'].append(execution_time)
        # calculate the mean and standard deviation
        mean = sum(stats['execution_time']) / sample_size
        std = stdev(stats['execution_time'])
        logger.info(f"Profiling finished. Mean: {mean}, Standard Deviation: {std}, Sample Size: {sample_size}")
        return mean, std, sample_size
