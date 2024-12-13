# data/deployment.py
from pymysql.connections import Connection
from typing import List
from model.deployments import Deployments
from db.connections import get_mediploy_connection
from fastapi import Depends
from error import Missing, Duplicate

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
def insert_deployment(hospital_id: int, reservation_time, version_id: int, conn: Connection):
    logger.debug("Starting insert_deployment data method")
    query = """
    INSERT INTO deployments (hospitalId, reservationTime, versionId, deployStatus)
    VALUES (%s, %s, %s, 1)
    """

    logger.debug(
        f"Executing query: {query} with parameters: hospital_id={hospital_id}, "
        f"reservation_time={reservation_time}, version_id={version_id}"
    )
    try :
        with conn.cursor() as cursor:
            cursor.execute(query, (hospital_id, reservation_time, version_id))
        conn.commit()

        logger.info(
            f"Deployment inserted successfully. "
            f"hospital_id={hospital_id}, reservation_time={reservation_time}, version_id={version_id}"
        )
    except Exception as e:
        logger.error(e)
        raise

# @with_connection
def delete_deployment(hospital_id: int, *, conn: Connection = Depends(get_mediploy_connection)):
    query = """
    DELETE FROM deployments
    WHERE hospitalId = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (hospital_id,))
    conn.commit()