# web/deployment.py
import logging
from fastapi import APIRouter, Depends
from service.deployVersions import DeployVersions
from fastapi import APIRouter
from pymysql.connections import Connection
from db.connections import get_mediploy_connection

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