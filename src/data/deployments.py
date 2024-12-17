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
def fetch_deployments(conn: Connection) -> List[Deployments]:
    logger.debug("Starting fetch_deployments data method")
    query = """
    SELECT 
        dm.deploymentId, dm.hospitalId, dv.versionId, dv.versionName, dm.reservationTime, dm.deployStatus, dm.createdAt, dm.updatedAt
    FROM deployments dm
    JOIN deployVersions dv 
    ON dm.versionId = dv.versionId
    """

    logger.debug(f"Executing query: {query}")

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    logger.debug(f"Query returned {len(results)} rows")

    # 결과를 Deployments 모델 리스트로 변환
    for row in results :
        print(row)
        print(type(row))
    deployments = [Deployments(**row) for row in results]
    logger.debug(f"Converted {len(deployments)} rows to Deployments models")
    
    return deployments

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