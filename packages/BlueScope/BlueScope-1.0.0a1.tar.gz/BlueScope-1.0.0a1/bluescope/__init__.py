from bluescope.db.consts import REDSHIFT_SERVERLESS
from bluescope.profiler import RedshiftServerlessProfiler

profiler_classes = {
    REDSHIFT_SERVERLESS: RedshiftServerlessProfiler,
}


def get_profiler(db_type):
    """ Get the connector for the given database type using mapping"""
    profiler_class = profiler_classes.get(db_type)
    if not profiler_classes:
        raise ValueError(f"Unsupported database type: {db_type}")
    return profiler_class