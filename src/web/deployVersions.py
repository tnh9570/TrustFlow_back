# web/deployment.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from service.deployVersions import DeployVersions
from fastapi import APIRouter
from pymysql.connections import Connection
from db.connections import get_mediploy_connection
from error import Duplicate

router = APIRouter(prefix="/deployVersions")
logger = logging.getLogger("app.web.deployVersions")

@router.get("")
# @router.get("/")
async def list_deployVersions(
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called")

    logger.debug(f"Calling DeploymentService.list_deployVersions)")
    result = await service.list_deployVersions(column_name=["versionId","versionName","filePath","SHA1Value","isNhnDeployment","createdAt"], conn=conn)
    return result

@router.get("/check")
# @router.get("/")
async def check_deployVersions(
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: check_deployVersions endpoint called")

    logger.debug(f"Calling DeploymentService.check_deployVersions)")
    result = await service.check_deployVersions()
    return result

@router.get(
    "/make/{versionName}",
    responses={
        200: {
            "description": "Successfully created or no conflicts.",
            "content": {"application/json": {"example": {"message": "complete"}}},
        },
        409: {
            "description": "Conflict: Version name already exists.",
            "content": {"application/json": {"example": {"detail": "exist versionName=vTEST, createdAt=2024-12-16 15:53:11"}}},
        },
    },
)
async def make_deployVersions(
    versionName: str,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called")

    logger.debug(f"Calling DeploymentService.list_deployVersions")
    try:
        await service.make_deployVersions(versionName=versionName, conn=conn)
        return "complete"
    except Duplicate as e :
        raise HTTPException(status_code=409, detail=str(e))
