# web/deployment.py
from fastapi import APIRouter, Depends
from service.deployments import DeploymentService
from datetime import datetime
import logging
from db.connections import get_mediploy_connection
from pymysql.connections import Connection
from error import Missing, Duplicate
from fastapi import APIRouter, HTTPException
from state import session_data

router = APIRouter(prefix="/deployments")
logger = logging.getLogger("app.web.deployments")

@router.get("")
@router.get("/")
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

@router.get("/{deploymentId}")
@router.get("/{deploymentId}/")
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

@router.post("")
@router.post("/")
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

@router.delete("/deployments/{hospitalId}")
async def cancel_deployment(hospitalId: int, service: DeploymentService = Depends()):
    await service.cancel_deployment(hospitalId)
    return {"message": "Deployment canceled"}