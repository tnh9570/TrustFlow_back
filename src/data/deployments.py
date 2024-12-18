# data/deployment.py
from pymysql.connections import Connection
from typing import List
from model.deployments import Deployments
from error import Missing
from state import CANCLED, RESERVED
import datetime
import logging
logger = logging.getLogger("app.data.deployments")

# def with_connection(func):
#     """
#     커넥션을 자동으로 관리하기 위한 데코레이터
#     """
#     def wrapper(*args, **kwargs):
#         conn = get_mediploy_connection()
#         try:
#             return func(*args, conn=conn, **kwargs)
#         finally:
#             conn.close()
#     return wrapper

# @with_connection
async def fetch_deployments(conn: Connection, page: int, size:int, sort: List[str], filters: dict[List]): # -> List[Deployments] 모델 값 하나 만들기
    logger.debug(f"Starting fetch_deployments data method with parameter page:{page} sort:{sort} filters:{filters} size:{size}")

# 
# localhost:8000/deployments?page=1&sort=createdAt:desc&sort=deployStatus:asc&filters=deployStatus:1&filters=hospitalId:c00075&filters=versionId:3

# status 라는 컬럼이 없어서 status 빼고 처리하는 쿼리 예시
# localhost:8000/deployments?page=1&sort=createdAt:desc&sort=deployStatus:asc&filters=status:success&filters=hospitalId:c00075&filters=versionId:3
    base_query = """
    SELECT 
        dm.deploymentId, dm.hospitalId, dv.versionId, dv.versionName, dm.reservationTime, dm.deployStatus, dm.createdAt, dm.updatedAt
    FROM deployments dm
    JOIN deployVersions dv 
    ON dm.versionId = dv.versionId 
    """

    # filter 조건 생성
    allow_filter_columns = {
        "hospitalId": "dm.hospitalId",
        "versionId": "dv.versionId",
        "deployStatus": "dm.deployStatus"
    }

    filter_result = "WHERE 1 "
    if filters:
        filter_query_params = []  # 바인딩할 파라미터 값을 저장할 리스트
        del_list = []
        
        for column, value in filters.items():
            if column in allow_filter_columns:
                placeholders = ", ".join(["%s"] * len(value))  # IN 절의 플레이스홀더 생성
                filter_result += f"AND {allow_filter_columns[column]} IN ({placeholders}) "
                filter_query_params.extend(value)  # 바인딩 값 추가
            else:
                del_list.append(column)

        for li in del_list:
            del filters[li]

        logger.debug(f"Executing query: {filter_result}")
        logger.debug(f"Executing query parameters: {filter_query_params}")

    allow_sort_columns={
        "deploymentId":"dm.deploymentId",
        "hospitalId":"dm.hospitalId",
        "versionId":"dv.versionId",
        "versionName":"dv.versionName",
        "reservationTime":"dm.reservationTime",
        "deployStatus":"dm.deployStatus",
        "createdAt":"dm.createdAt",
        "updatedAt":"dm.updatedAt"
    }
    allow_sort_directions=["desc","asc"]

    if sort:
        sort_query_params = []
        for item in sort:
            column, direction = item.split(":")
            # direction을 소문자로 변환 후 검증
            direction = direction.lower()
            if column in allow_sort_columns and direction in allow_sort_directions:
                sort_query_params.append(f"{column} {direction.upper()}")
        
        sort_result = " ORDER BY "+", ".join(sort_query_params)

    
    # 함수로 만들 때 return ", ".join(sort_result)
    logger.debug(f"Executing query: {sort_result}")

    offset = (page - 1) * size
    limit = size
    offset_query = " LIMIT %s OFFSET %s"
    
    count_query = """
        SELECT COUNT(*) 
        FROM deployments dm
        JOIN deployVersions dv 
        ON dm.versionId = dv.versionId
        """ + filter_result
    # 전체 개수 가져오기
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

    # 결과를 Deployments 모델 리스트로 변환
    for row in results :
        print(row)
        print(type(row))
    deployments = [Deployments(**row) for row in results]
    logger.debug(f"Converted {len(deployments)} rows to Deployments models")
    
    
    logger.debug(f"Total count: {total_count}")

    return {"data": deployments, "page": {"totalPages":total_count}}

# @with_connection
def fetch_deployment_detail(conn: Connection, deploymentId: int) -> Deployments:
    logger.debug("Starting fetch_deployment_detail data method")
    query = """
    SELECT 
        dm.deploymentId, dm.hospitalId, dv.versionId, dv.versionName, dm.reservationTime, dm.deployStatus, dm.createdAt, dm.updatedAt
    FROM deployments dm
    JOIN deployVersions dv 
    ON dm.versionId = dv.versionId
    WHERE dm.deploymentId = %s
    """

    logger.debug(f"Executing query: {query}")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (deploymentId,))
            results = cursor.fetchone()
        
        logger.debug(f"Query returned {results} rows")
    
        return Deployments(**results)
    except Exception as e:
        logger.error(e)
        raise Missing(msg=f"Deployment with ID {deploymentId} not found")

# @with_connection
def create_deployment(hospitalId: str, reservationTime: datetime, versionId: int, conn: Connection):
    """
    배포 예약을 데이터베이스에 삽입하는 함수.

    Args:
        hospitalId (str): 병원 ID.
        reservationTime (datetime): 예약 시간.
        versionId (int): 배포 버전 ID.
        conn (Connection): 데이터베이스 연결 객체.
    """
    logger.debug("Starting create_deployment data method")
    query = """
    INSERT INTO deployments (hospitalId, reservationTime, versionId, deployStatus)
    VALUES (%s, %s, %s, 1)
    """
    logger.debug(
        f"Executing query: {query} with parameters: "
        f"hospitalId={hospitalId}, reservationTime={reservationTime}, versionId={versionId}"
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (hospitalId, reservationTime, versionId))
        conn.commit()
        logger.info("Deployment inserted successfully.")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


def fetch_target_ids(deployment_ids: list[int], conn: Connection) -> list[int]:
    """
    현재 상태가 RESERVED인 업데이트 대상 ID 가져오기.
    
    Args:
        deployment_ids (list[int]): 요청된 배포 ID 리스트.
        conn (Connection): 데이터베이스 연결 객체.

    Returns:
        list[int]: 업데이트 대상 ID 리스트.
    """
    logger.debug("Starting fetch_target_ids data method")
    placeholders = ",".join(["%s"] * len(deployment_ids))
    query = f"""
    SELECT deploymentId 
    FROM deployments 
    WHERE deploymentId IN ({placeholders}) 
    AND deployStatus = {RESERVED};
    """
    logger.debug(f"Executing SELECT query: {query} with IDs: {deployment_ids}")
    
    with conn.cursor() as cursor:
        cursor.execute(query, deployment_ids)
        result = [row['deploymentId'] for row in cursor.fetchall()]
    
    logger.debug(f"Target IDs fetched: {result}")
    
    return result


def update_deployments_to_canceled(target_ids: list[int], conn: Connection):
    """
    대상 ID의 상태를 CANCELED로 업데이트.
    
    Args:
        target_ids (list[int]): 업데이트 대상 ID 리스트.
        conn (Connection): 데이터베이스 연결 객체.
    """
    logger.debug("Starting update_deployments_to_canceled data method")

    if not target_ids:
        logger.info("No target IDs provided for update.")
        return

    placeholders = ",".join(["%s"] * len(target_ids))
    query = f"""
    UPDATE deployments 
    SET deployStatus = %s 
    WHERE deploymentId IN ({placeholders});
    """
    params = [CANCLED] + target_ids
    logger.debug(f"Executing UPDATE query: {query} with params: {params}")
    
    with conn.cursor() as cursor:
        cursor.execute(query, params)
    conn.commit()
    
    logger.debug(f"Updated rows count: {cursor.rowcount}")