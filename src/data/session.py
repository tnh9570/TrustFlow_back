# data/deployment.py
from pymysql.connections import Connection
from typing import List
from db.connections import get_mediploy_connection
from fastapi import Depends
from error import Missing, Duplicate
import logging

logger = logging.getLogger("app.data.session")

def fetch_DBNAMES(conn: Connection) :
    logger.debug("Starting fetch_DBNAMES data method")
    query = """
    SELECT DBNAME as hospitalName 
    FROM TMEDICHISUSER
    """

    logger.debug(f"Executing query: {query}")
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        
        logger.debug(f"Query returned {results} rows")
        return [row['hospitalName'] for row in results]

    except Exception as e:
        logger.error(e)
        raise