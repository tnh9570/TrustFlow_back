import logging
import json
from pymysql.connections import Connection
from model.deployVersions import DeployVersions
from state import session_data

from data.deployVersions import (
    fetch_deployVersions,
)


class DeployVersions:
    def __init__(self):
        self.logger = logging.getLogger("app.service.DeployVersions")

    async def list_deployVersions(self, column_name: list, conn: Connection) -> list[DeployVersions]:
        """
        특정 컬럼 데이터를 기반으로 배포 버전을 조회하고, session_data를 병합하여 반환.
        
        Args:
            column_name (list) : 조회할 컬럼
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            str: 배포 버전 결과와 session_data를 포함한 JSON 문자열.
        """
        self.logger.debug(f"Starting list_deployVersions service method for column_name: {column_name}")
        
        self.logger.debug(f"Fetching fetch_deployVersions for column_name: {column_name}")
        result = fetch_deployVersions(column_name=column_name,conn=conn)

        self.logger.debug(f"Retrieved {len(result)} DeployVersions")

        # 병합 데이터 생성
        merged_data = {
            "versions": result,
            "hospitals": session_data,
        }

        self.logger.debug(f"Merged data: {merged_data}")

        return merged_data
        