import logging

from pymysql.connections import Connection
from typing import List
from model.deployVersions import DeployVersions
from utils import build_filter_query, build_sort_query, calculate_pagination

logger = logging.getLogger("app.data.deployVersions")

async def fetch_deployVersions(column_name:list, conn: Connection, page: int, size:int, sort: List[str], filters: dict[List]) -> List[DeployVersions]:
    logger.debug("Starting fetch_deployVersions data method")
    base_query = f"""
    SELECT 
        *
    FROM deployVersions 
    """

    filter_result = "WHERE 1 "
    allow_filter_columns = {
        "versionId":"versionId",
        "versionName":"versionName",
        "filePath":"filePath",
        "SHA1Value":"SHA1Value",
        "isNhnDeployment":"isNhnDeployment",
        "createdAt":"createdAt"
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

    deployVersions = [DeployVersions(**row) for row in results]

    logger.debug(f"Total count: {total_count}")

    return {"data": deployVersions, "page": {"totalPages":total_count}}

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
    
