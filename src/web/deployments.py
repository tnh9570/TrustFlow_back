# web/deployment.py
import logging

from typing import List, Optional
from fastapi import APIRouter, Depends, APIRouter, HTTPException, Query
from service.deployments import DeploymentService
from service.deployVersions import DeployVersions
from service.hospital import HospitalsService 
from db.connections import get_mediploy_connection
from pymysql.connections import Connection
from error import Missing
from state import session_data
from model.deployments import DeploymentCreate, DeploymentsCancled

router = APIRouter(prefix="/deployments")
logger = logging.getLogger("app.web.deployments")

@router.get("", include_in_schema=False)
@router.get("/")
async def list_deployments(
    # 페이지네이션 파라미터
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    size: int = Query(15, ge=1, le=100, description="Number of items per page (default: 15)"),
    
    # 정렬 파라미터
    # sort: Optional[List[str]] = Query(
    #     ["deploymentId:desc"],
    #     title="Sort Fields",
    #     description="List of fields to sort by with order (e.g., deploymentId:desc,name:asc)"
    # ),
    # 필터 조건 (예: hospitalId:c00075,status:active)
    sort: List[str] = Query(["deploymentId:desc"], description="정렬 기준과 순서"),
    filters: Optional[List[str]] = Query(None, description="필터링 조건, 예: filter=status:success"),

    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends()
):
    """
    필터링, 정렬 및 페이지네이션이 적용된 배포 목록 조회 API.
    - page: 페이지 번호
    - sort: 정렬 기준 (여러 개 지원)
    - filters: 필터링 조건. 형식: '칼럼명:값' (예: status:success)
    """
    logger.debug("GET: list_deployments endpoint called")

    # Connection 상태 로그
    logger.debug(f"Connection object: {conn}")
        
    # 서비스 호출 로그
    logger.debug("Calling DeploymentService.list_deployments()")
    deployments = await service.list_deployments(conn=conn, page=page, size=size, sort=sort, filters=filters)

    # 결과 로그
    logger.debug(f"DeploymentService.list_deployments() returned {len(deployments)} items")
    return deployments

@router.get("/inform", include_in_schema=False)
@router.get("/inform/") # 같은 / 경로에 있을 때 정적 주소가 동적 주소보다 먼저 동작하기 떄문에 정적주소를 먼저 작성
async def list_deployVersions(
    conn: Connection = Depends(get_mediploy_connection),
    serviceDeploy: DeployVersions = Depends(),
    servicehospital: HospitalsService = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called")

    logger.debug(f"Calling DeploymentService.list_deployVersions)")
    versions = await serviceDeploy.list_deployVersions(column_name=["versionId", "versionName"], conn=conn)
    hospitals = await servicehospital.list_hospitals()
    # 병합 데이터 생성
    merged_data = {
        "versions": versions,
        "hospitals": hospitals,
    }
    return merged_data

@router.get("/{deploymentId}")
async def get_deployment_detail(
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
        deployment = await service.deployment_detail(deploymentId, conn)
        
        # 결과 로그
        logger.debug(f"deployment_detail for deploymentId={deploymentId}: {deployment}")
        return deployment
    
    except Missing as exc:
        logger.warning(f"Deployment ID {deploymentId} not found: {exc}")
        raise HTTPException(status_code=404, detail="Deployment not found")

@router.post("/create", include_in_schema=False)
@router.post("/create/")
async def createDeployment(
    request: DeploymentCreate,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends()
):
    """
    배포 예약 API 엔드포인트.

    Args:
        request (DeploymentCreate): 예약 요청 데이터.
        conn (Connection): 데이터베이스 연결 객체.
        service (DeploymentService): 배포 서비스 객체.

    Returns:
        dict: 성공 메시지.
    """
    logger.info("POST: /create endpoint called")
    logger.debug(f"Request data: {request}")

    try:
        await service.create_deployment(
            hospitalId=request.hospitalId,
            reservationTime=request.reservationTime,
            versionId=request.versionId,
            immediately=request.immediately,
            conn=conn
        )
        return {"message": "Deployment reserved successfully"}
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
@router.put("/cancled", include_in_schema=False)
@router.put("/cancled/")
async def cancel_deployments(
    request: DeploymentsCancled,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeploymentService = Depends(),
):
    logger.info(f"PUT: cancel_deployments: endpoint called with data: {request}")
    try:
        result = await service.cancel_deployments(deploymentIds = request.deploymentIds, conn = conn)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in cancel_deployment: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while cancelling deployments.")