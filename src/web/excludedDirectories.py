# web/excludedDirectories.py
import logging

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from service.excludedDirectories import excludedDirectoriesService
from fastapi import APIRouter, Query
from pymysql.connections import Connection
from db.connections import get_mediploy_connection
from model.excludedDirectories import ExcludedDirectoriesCreate, ExcludedDirectoriesDelete

router = APIRouter(prefix="/except")
logger = logging.getLogger("app.web.excludedDirectories")

@router.get("", include_in_schema=False)
@router.get("/")
async def get_excludedDirectories(
    # 페이지네이션 파라미터
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    size: int = Query(15, ge=1, le=100, description="Number of items per page (default: 15)"),
    sort: List[str] = Query(["directoryId:desc"], description="정렬 기준과 순서"),
    filters: Optional[List[str]] = Query(None, description="필터링 조건, 예: filter=status:success"),

    conn: Connection = Depends(get_mediploy_connection),
    service: excludedDirectoriesService = Depends()
):
    logger.debug(f"GET: list_excludedDirectories endpoint called")

    result = await service.get_excludedDirectories(conn=conn, page=page, size=size, sort=sort, filters=filters)
    return result

@router.post("/create", include_in_schema=False)
@router.post("/create/")
async def create_excludedDirectories(
    request: ExcludedDirectoriesCreate,
    conn: Connection = Depends(get_mediploy_connection),
    service: excludedDirectoriesService = Depends()
):
    """
    배포제외디렉토리 관리 API 엔드포인트.

    Args:
        request (excludedDirectoriesCreate): 예약 요청 데이터.
        conn (Connection): 데이터베이스 연결 객체.
        service (excludedDirectoriesService): 배포 서비스 객체.

    Returns:
        dict: 성공 메시지.
    """
    logger.info("create_excludedDirectories endpoint called")
    logger.debug(f"Request data: {request}")

    try:
        await service.create_excludedDirectories(
            directoryPath=request.directoryPath,
            reason=request.reason,
            conn=conn
        )
        return {"message": "excludedDirectories reserved successfully"}
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
@router.delete("/delete", include_in_schema=False)
@router.delete("/delete/")
async def delete_excludedDirectories(
    request: ExcludedDirectoriesDelete,
    conn: Connection = Depends(get_mediploy_connection),
    service: excludedDirectoriesService = Depends()
):
    """
    배포제외디렉토리 삭제 API 엔드포인트.

    Args:
        request.directoryIds (list[int]): 삭제할 배포 디렉토리 Id List
        conn (Connection): 데이터베이스 연결 객체.
        service (excludedDirectoriesService): 배포 서비스 객체.

    Returns:
        dict: 성공 메시지.
    """
    logger.info(f"delete_excludedDirectories endpoint called with request: {request}")
    try:
        await service.delete_excludedDirectories(
            directoryIds=request.directoryIds,
            conn=conn
        )
        return {"message": "excludedDirectories reserved successfully"}
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    