from pymysql.connections import Connection
from typing import List
from model.deployVersions import DeployVersions

import logging
logger = logging.getLogger("app.data.deployVersions")

def fetch_deployVersions(column_name:list, conn: Connection) -> List[DeployVersions]:
    logger.debug("Starting fetch_deployVersions data method")
    query = f"""
    SELECT 
        {",".join(column_name)}
    FROM deployVersions 
    """

    logger.debug(f"Executing query: {query}")

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    logger.debug(f"Query returned {len(results)} rows")

    return results
