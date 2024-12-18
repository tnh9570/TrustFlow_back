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
        f"Executing query: {query} with parameters: versionName: {versionName}, SHA1Value: {SHA1Value}"
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

async def update_deployVersions(versionId: int, conn: Connection):
    logger.debug("Starting update_deployVersions data method")
    
    query = """
    UPDATE deployVersions
    SET isNhnDeployment = CASE
        WHEN versionId = %s THEN 1
        ELSE 0
    END;
    """
    
    logger.debug(f"Executing query with parameters: versionId={versionId}")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (versionId,))
            logger.debug("Query executed successfully")
        
        conn.commit()
        logger.info(f"deployVersions updated successfully for versionId={versionId}")
    except Exception as e:
        logger.error(f"Error executing update_deployVersions: {e}")
        raise e
    
async def delete_deployVersions(versionId: List[int], conn: Connection):
    logger.debug("Starting delete_deployVersions data method")
    
    placeholders = ",".join(["%s"] * len(versionId))

    query = f"""
    DELETE FROM deployVersions
    WHERE versionId IN ({placeholders}) ;
    """
    
    logger.debug(f"Executing query with parameters: versionId={versionId}")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(versionId))
            logger.debug("Query executed successfully")
        
        conn.commit()
        logger.info(f"deployVersions updated successfully for versionId={versionId}")
    except Exception as e:
        logger.error(f"Error executing delete_deployVersions: {e}")
        raise e
    
