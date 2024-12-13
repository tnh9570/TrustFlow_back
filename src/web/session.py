# web/deployment.py
from fastapi import APIRouter, Depends
from service.session import SessionService
from datetime import datetime
import logging
from db.connections import get_mms_connection
from pymysql.connections import Connection
from error import Missing, Duplicate
from fastapi import APIRouter, HTTPException
from state import session_data

router = APIRouter(prefix="/session")
logger = logging.getLogger("app.web.session")

@router.get("/set")
@router.get("/set/")
async def set_session(
    conn: Connection = Depends(get_mms_connection),
    service: SessionService = Depends()
):
    logger.debug("GET: set_session endpoint called")

    # Connection 상태 로그
    logger.debug(f"Connection object: {conn}")
    # 서비스 호출 로그
    logger.debug("Calling SessionService.list_medichis_db()")
    db_names = await service.list_medichis_db(conn)

    logger.debug("Calling SessionService.list_medichis_names()")
    results = await service.list_medichis_names(db_names)
    
    session_data.update(results['success'])
    print("@@@@@@@@@@@@@@@@")
    logger.debug(f"session_data : {session_data}")
    return "COMPLETE"

@router.get("/get")
@router.get("/get/")
def get_sesssion():
    return session_data