# web/deployment.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from service.deployVersions import DeployVersions
from fastapi import APIRouter
from pymysql.connections import Connection
from db.connections import get_mediploy_connection
from error import Duplicate
from model.deployVersions import DeployVersionCreate

router = APIRouter(prefix="/deployVersions")
logger = logging.getLogger("app.web.deployVersions")

@router.get("", include_in_schema=False)
@router.get("/")
async def list_deployVersions(
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called")

    result = await service.list_deployVersions(column_name=["versionId","versionName","filePath","SHA1Value","isNhnDeployment","createdAt"], conn=conn)
    return result

@router.get("/check", include_in_schema=False)
@router.get("/check/")
# @router.get("/")
async def check_deployVersions(
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: check_deployVersions endpoint called")

    result = await service.check_deployVersions()
    return result

@router.post("/create", include_in_schema=False)
@router.post(
    "/create/",
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
    request: DeployVersionCreate,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):
    logger.debug(f"GET: list_deployVersions endpoint called with versionName: {request.versionName}")

    try:
        await service.make_deployVersions(versionName=request.versionName, conn=conn)
        return "complete"
    except Duplicate as e :
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/deployNHN/{versionId}")
async def NHN_deployVersions(
    versionId: int,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):  
    logger.debug(f"GET: NHN_deployVersions endpoint called with versionId: {versionId}")
    try :
        await service.NHN_deployVersions(versionId=versionId, conn=conn)
    except Exception as e :
        raise HTTPException(status_code=404, detail=str(e)) 
    return "complete"

@router.delete("/delete/{versionId}")
async def delete_deployVersions(
    versionId: int,
    conn: Connection = Depends(get_mediploy_connection),
    service: DeployVersions = Depends()
):  
    logger.debug(f"GET: delete_deployVersions endpoint called with versionId: {versionId}")
    try :
        await service.delete_deployVersions(versionId=versionId, conn=conn)
    except Exception as e :
        raise HTTPException(status_code=404, detail=str(e)) 
    return "complete"