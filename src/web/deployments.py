# web/deployment.py
import logging

from typing import List
from fastapi import APIRouter, Depends, APIRouter, HTTPException, Query
from service.deployments import DeploymentService
from service.deployVersions import DeployVersions
from datetime import datetime
from db.connections import get_mediploy_connection
from pymysql.connections import Connection
from error import Missing, Duplicate
from state import session_data

router = APIRouter(prefix="/deployments")
logger = logging.getLogger("app.web.deployments")

@router.get("")
async def list_deployments(
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends()
):
    logger.debug("GET: list_deployments endpoint called")

    # Connection 상태 로그
    logger.debug(f"Connection object: {conn}")
        
    # 서비스 호출 로그
    logger.debug("Calling DeploymentService.list_deployments()")
    deployments = await service.list_deployments(conn)

    # 결과 로그
    logger.debug(f"DeploymentService.list_deployments() returned {len(deployments)} items")
    return deployments

@router.get("/preDeploy") # 같은 / 경로에 있을 때 정적 주소가 동적 주소보다 먼저 동작하기 떄문에 정적주소를 먼저 작성
async def list_deployVersions(
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called")

    logger.debug(f"Calling DeploymentService.list_deployVersions)")
    result = await service.list_deployVersions(column_name=["versionId", "versionName"], conn=conn)
    
    # 병합 데이터 생성
    merged_data = {
        "versions": result,
        "hospitals": session_data,
    }
    return merged_data

@router.get("/{deploymentId}")
async def deployment_detail(
    deploymentId: int,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends()
):
    try:
        # 요청 로그
        logger.debug(f"GET: deployment_detail endpoint called with deploymentId={deploymentId}")
        
        # Connection 상태 로그
        logger.debug(f"Connection object: {conn}")
        
        # 서비스 호출 로그
        logger.debug(f"Calling DeploymentService.deployment_detail(deploymentId={deploymentId})")
        deployment = await service.deployment_detail(deploymentId, conn)
        
        # 결과 로그
        logger.debug(f"deployment_detail for deploymentId={deploymentId}: {deployment}")
        return deployment
    
    except Missing as exc:
        logger.warning(f"Deployment ID {deploymentId} not found: {exc}")
        raise HTTPException(status_code=404, detail="Deployment not found")

@router.post("/reservation")
async def reserve_deployment(
    hospitalId: str, reservationTime: datetime, versionId: int,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends()
):
    # 요청 시작 로그
    logger.debug(f"POST: reserve_deployment endpoint called")
    logger.debug(f"POST: Input data - hospitalId={hospitalId}, reservationTime={reservationTime}, versionId={versionId}")

    # 서비스 호출 로그
    logger.debug(f"Calling DeploymentService.reserve_deployment)")
    await service.reserve_deployment(hospitalId, reservationTime, versionId, conn)
    return {"message": "Deployment reserved"}

@router.put("/cancled/{dId}")
async def cancel_deployments(
    dIds: List[int] = Query(
        ...,  # 필수 파라미터
        title="Deployment IDs",  # 파라미터 설명
        description="List of deployment IDs to cancel",  # 상세 설명
        example=[1, 2, 3],  # Swagger UI에서 표시할 예제
    ),
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends(),
):
    logger.debug(f"PUT: cancel_deployments endpoint called")
    logger.debug(f"POST: Input data - deploymentId={dIds}")

    logger.debug(f"Calling DeploymentService.cancel_deployments")
    await service.cancel_deployments(deploymentIds = dIds, conn = conn)
    return {"message": "Deployment canceled"}