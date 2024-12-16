# web/deployment.py
from fastapi import APIRouter, Depends
from service.hospital import HospitalsService
import logging
from fastapi import APIRouter

router = APIRouter(prefix="/hospitals")
logger = logging.getLogger("app.web.hospitals")

@router.get("")
# @router.get("/")
async def list_hospitals(
    service: HospitalsService = Depends()
):
    logger.debug("GET: list_hospitals endpoint called")

    # 서비스 호출 로그
    logger.debug("Calling HospitalsService.list_hospitals()")
    hospitals = service.list_hospitals()

    # 결과 로그
    logger.debug(f"HospitalsService.list_hospitals() returned {len(hospitals)} items")
    
    return hospitals