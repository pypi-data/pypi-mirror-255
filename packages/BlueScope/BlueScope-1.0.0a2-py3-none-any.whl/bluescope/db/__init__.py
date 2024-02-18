from bluescope.db.consts import REDSHIFT_SERVERLESS
from bluescope.db.redshift import RedshiftServerlessConnection

connector_classes = {
    REDSHIFT_SERVERLESS: RedshiftServerlessConnection,
}


def get_connector(db_type, **kwargs):
    """ Get the connector for the given database type using mapping"""
    connector_class = connector_classes.get(db_type)
    if not connector_class:
        raise ValueError(f"Unsupported database type: {db_type}")
    return connector_class(**kwargs)
