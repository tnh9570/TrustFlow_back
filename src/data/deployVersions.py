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
    
    query1 = "UPDATE deployVersions SET isNhnDeployment = 0 WHERE isNhnDeployment = 1;"
    query2 = "UPDATE deployVersions SET isNhnDeployment = 1 WHERE versionId = %s;"
    
    logger.debug(f"Executing queries with parameters: versionId={versionId}")
    
    try:
        with conn.cursor() as cursor:
            # 첫 번째 쿼리 실행
            cursor.execute(query1)
            logger.debug("Query1 executed successfully")

            # 두 번째 쿼리 실행
            cursor.execute(query2, (versionId,))
            logger.debug("Query2 executed successfully")
        
        conn.commit()
        logger.info(f"deployVersions updated successfully for versionId={versionId}")
    except Exception as e:
        logger.error(f"Error executing update_deployVersions: {e}")
        raise e
