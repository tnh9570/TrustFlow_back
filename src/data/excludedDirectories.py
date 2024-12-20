import logging

from pymysql.connections import Connection
from typing import List
from model.excludedDirectories import ExcludedDirectories
from utils import build_filter_query, build_sort_query, calculate_pagination

logger = logging.getLogger("app.data.excludedDirectories")

async def get_excludedDirectories(conn: Connection, page: int, size:int, sort: List[str], filters: dict[List]) -> List[ExcludedDirectories]:
    logger.debug("Starting get_excludedDirectories data method")
    base_query = f"""
    SELECT 
        *
    FROM excludedDirectories 
    """
    filter_result = "WHERE 1 "
    allow_filter_columns = {
        "directoryId":"directoryId",
        "directoryPath":"directoryPath",
        "reason":"reason",
        "crtime":"crtime",
    }
    if filters:
        filter_result, filter_query_params = build_filter_query(filter_result=filter_result, filters=filters, allow_filter_columns=allow_filter_columns)

    allow_sort_columns = allow_filter_columns
    allow_sort_directions=["desc","asc"]

    if sort:
        sort_result = build_sort_query(sort_result=sort, sorts=sort, allow_sort_columns=allow_sort_columns, allow_sort_directions=allow_sort_directions)

    offset, limit = calculate_pagination(page=page, size=size)

    offset_query = " LIMIT %s OFFSET %s"
    
    # 전체 개수 가져오기
    count_query = """
        SELECT COUNT(*) 
        FROM deployVersions 
        """ + filter_result

    if filters :
        query_params = list(filter_query_params)
    else :
        query_params = []     

    with conn.cursor() as cursor:
        cursor.execute(count_query, query_params)
        total_count = cursor.fetchone()['COUNT(*)']
        logger.debug(f'total_count = {total_count}')

    with conn.cursor() as cursor:
        cursor.execute(base_query + filter_result + sort_result + offset_query, query_params + [limit, offset])
        results = cursor.fetchall()

    logger.debug(f"Query returned {len(results)} rows")

    excludedDirectories = [ExcludedDirectories(**row) for row in results]

    logger.debug(f"Total count: {total_count}")

    return {"data": excludedDirectories, "page": {"totalPages":total_count}}

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