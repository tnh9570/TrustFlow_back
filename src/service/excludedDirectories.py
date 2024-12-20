import logging
from pymysql.connections import Connection
from model.excludedDirectories import ExcludedDirectories
from typing import List
from utils import parse_filters

from data.excludedDirectories import (
    get_excludedDirectories,
    create_excludedDirectories,
    delete_excludedDirectories
)


class excludedDirectoriesService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.excludedDirectories")

    async def get_excludedDirectories(self, conn: Connection, page: int, size: int, sort: List[str], filters: List[str]) -> list[ExcludedDirectories]:
        """
        배포제외디렉토리 리스트 불러오기
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            list[ExcludedDirectories]
        """
        self.logger.debug(f"Starting get_excludedDirectories service method")
        
        query_filters = parse_filters(filters)

        result = await get_excludedDirectories(conn=conn, page=page, size=size, sort=sort, filters=query_filters)

        self.logger.debug(f"Retrieved {len(result)} excludedDirectories")

        return result
    
    async def create_excludedDirectories(self, directoryPath: str, reason: str, conn: Connection):
        """
        배포제외디렉토리 추가 로직.

        Args:
            directoryPath (str): 배포제외 디렉토리.
            reason (str): 배포 버전 ID.
            conn (Connection): 데이터베이스 연결 객체.
        """
        self.logger.info(f"Starting create_excludedDirectories service method. \
                            Input data: directoryPath={directoryPath}, reason={reason}")
        
        # 데이터 계층 호출
        try:
            create_excludedDirectories(directoryPath, reason, conn)
        except Exception as e:
            self.logger.error(f"Error in create_excludedDirectories: {e}")
            raise
    
    async def delete_excludedDirectories(self, directoryId: int, conn: Connection):
        """
        배포제외디렉토리 추가 로직.

        Args:
            directoryId (str): 배포제외 디렉토리.
            conn (Connection): 데이터베이스 연결 객체.
        """
        self.logger.info(f"Starting delete_excludedDirectories service method. \
                            Input data: directoryId={directoryId}")
        
        # 데이터 계층 호출
        try:
            delete_excludedDirectories(directoryId, conn)
        except Exception as e:
            self.logger.error(f"Error in delete_excludedDirectories: {e}")
            raise