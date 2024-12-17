# service/deployment.py
from pymysql.connections import Connection
import logging
import httpx
import asyncio
from config import settings

from data.session import (
    fetch_DBNAMES,
)


class SessionService:
    """
    SessionService 클래스는 mms_connection 을 통해,
    medicihs 병원 이름을 세션에 데이터를 저장하는 비즈니스 로직을 처리합니다.
    """

    def __init__(self):
        self.logger = logging.getLogger("app.service.SessionService")

    async def list_medichis_db(self, conn: Connection):
        """
        Medichis 데이터베이스 이름 목록을 가져오는 메서드.
        데이터를 `data` 계층(fetch_DBNAMES 함수)에서 조회.
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            list: 데이터베이스 이름의 목록.
        """
        self.logger.debug("Starting list_medichis_db_names service method")
        
        # 데이터베이스 이름 조회 시작
        self.logger.debug("Fetching session from data layer")
        db_names = fetch_DBNAMES(conn)

        # 결과 로그
        self.logger.debug(f"Retrieved {len(db_names)} database names: {db_names}")
        return db_names
    
    async def list_medichis_names(self, db_names : list):
        """
        여러 데이터베이스 이름을 기반으로 비동기 요청을 보내 각 데이터베이스의 병원 이름(HOSPNAME)을 가져옴.
        
        Args:
            db_names (list): 데이터베이스 이름 목록.

        Returns:
            dict: 성공적인 응답과 에러를 포함한 딕셔너리.
                  {"success": 성공적으로 가져온 데이터, "errors": 발생한 에러들}
        """
        self.logger.debug("Starting list_medichis_names service method")

        headers = {
            "Authorization": settings.MMS_AUTHORIZATION
        }

        # 요청할 URL 목록 생성
        urls = {db_name: f"https://{db_name}.medichis.com/internal/customer" for db_name in db_names}
        
        try:
            async with httpx.AsyncClient() as client:
                # 비동기 작업 생성
                tasks = {db_name: client.get(url, headers=headers) for db_name, url in urls.items()}
                self.logger.debug(f"Created async tasks for {len(tasks)} URLs")

                # 예외를 반환하도록 설정
                responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
                
                # 성공적인 응답과 에러를 분리
                successful_responses = {}
                errors = []

                for db_name, response in zip(tasks.keys(), responses):
                    if isinstance(response, httpx.Response) and response.status_code == 200:
                    # 성공적인 응답 처리
                        try:
                            hosp_name = response.json()['data']['HOSPNAME']
                            self.logger.debug(f"Successful Response {db_name}: {hosp_name}")
                            successful_responses[db_name] = hosp_name
                        except (KeyError, ValueError) as e:
                            # JSON 파싱 실패
                            self.logger.error(f"ERROR Response {db_name}: {response.json()}")
                            errors.append({"db_name": db_name, "error": f"Parsing error: {e}"})
                    else:
                        # HTTP 응답 에러 또는 예외
                        self.logger.debug(f"db_name: {db_name}, error: {str(response)}")
                        errors.append({"db_name": db_name, "error": str(response)})
                        

                # 디버깅 로그
                self.logger.debug(f"Successful Responses: {successful_responses}")
                self.logger.debug(f"Errors: {errors}")

                return {"success": successful_responses, "errors": errors}
            
        except Exception as e:
            self.logger.error(f"Critical error: {e}")
            return {"success": [], "errors": [{"error": str(e)}]}
        