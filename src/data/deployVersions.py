from pymysql.connections import Connection
from typing import List
from model.deployVersions import DeployVersions

import logging
logger = logging.getLogger("app.data.deployVersions")

async def fetch_deployVersions(column_name:list, conn: Connection) -> List[DeployVersions]:
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

async def fetch_deployVersions_detail(versionName: str, conn: Connection):
    logger.debug("Starting fetch_deployVersions_detail data method")
    query = """
    SELECT 
        versionName, createdAt
    FROM deployVersions 
    where versionName=%s
    """

    logger.debug(f"Executing query: {query} with parameter versionName: {versionName}")

    with conn.cursor() as cursor:
        cursor.execute(query,versionName)
        result = cursor.fetchall()

    logger.debug(f"Query returned {result}")

    return result

async def insert_deployVersions(versionName: str, filpath: str, SHA1Value: str, conn: Connection):
    logger.debug("Starting insert_deployVersions data method")
    query = """
    INSERT INTO deployVersions (versionName, SHA1Value)
    VALUES (%s, %s)
    """

    logger.debug(
        f"Executing query: {query} with parameters: versionName={versionName}, SHA1Value={SHA1Value}"
    )
    try :
        with conn.cursor() as cursor:
            cursor.execute(query, (versionName, SHA1Value))
        conn.commit()

        logger.info(
            f"deployVersions inserted successfully. "
            f"versionName={versionName}, SHA1Value={SHA1Value}"
        )
    except Exception as e:
        logger.error(e)
        raise e