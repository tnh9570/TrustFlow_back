from pymysql.connections import Connection
from typing import List
from model.excludedDirectories import ExcludedDirectories
from datetime import datetime
import logging

logger = logging.getLogger("app.data.excludedDirectories")

async def get_excludedDirectories(conn: Connection) -> List[ExcludedDirectories]:
    logger.debug("Starting get_excludedDirectories data method")
    query = f"""
    SELECT 
        *
    FROM excludedDirectories 
    """

    logger.debug(f"Executing query: {query}")

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    logger.debug(f"Query returned {len(results)} rows")

    return [ExcludedDirectories(**row) for row in results]

def create_excludedDirectories(directoryPath: str, reason: str, conn: Connection):
    """
    배포제외 디렉토리을 데이터베이스에 삽입하는 함수.

    Args:
        directoryPath (str): 배포제외 디렉토리.
        reason (str): 배포 버전 ID.
        conn (Connection): 데이터베이스 연결 객체.
    """

    logger.debug("Starting create_excludedDirectories data method")

    query = """
    INSERT INTO excludedDirectories (directoryPath, reason)
    VALUES (%s, %s)
    """
    logger.debug(
        f"Executing query: {query} with parameters: "
        f"directoryPath={directoryPath}, reason={reason}"
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (directoryPath, reason))
        conn.commit()
        logger.info("excludedDirectories inserted successfully.")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise

def delete_excludedDirectories(directoryId: int, conn: Connection):
    """ 
    배포제외 디렉토리 삭제
    Args:
        directoryPath (str): 배포제외 디렉토리.
        reason (str): 배포 버전 ID.
        conn (Connection): 데이터베이스 연결 객체.
    Returns:

    """

    logger.debug("Starting delete_excludedDirectories data method")

    query = """
    DELETE FROM excludedDirectories WHERE directoryId= %s;
    """
    logger.debug(
        f"Executing query: {query} with parameters: {directoryId}"
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (directoryId, ))
        conn.commit()
        logger.info("excludedDirectories delete successfully.")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise