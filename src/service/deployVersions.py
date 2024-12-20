import logging
from pymysql.connections import Connection
from model.deployVersions import DeployVersions
from error import Duplicate
from typing import List
from utils import parse_filters

from data.deployVersions import (
    fetch_deployVersions,
    get_deployVersions_with_versionName,
    fetch_deployVersions_detail,
    insert_deployVersions,
    update_deployVersions,
    delete_deployVersions
)


class DeployVersions:
    def __init__(self):
        self.logger = logging.getLogger("app.service.DeployVersions")

    async def list_deployVersions(self, conn: Connection, page: int, size: int, sort: List[str], filters: List[str]) -> list[DeployVersions]:
        """
        특정 컬럼 데이터를 기반으로 배포 버전을 조회하고, session_data를 병합하여 반환.
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            str: 배포 버전 결과와 session_data를 포함한 JSON 문자열.
        """
        self.logger.debug(f"Starting list_deployVersions service method")
        
        query_filters = parse_filters(filters)

        self.logger.debug(f"Fetching fetch_deployVersions")
        result = await fetch_deployVersions(conn=conn, page=page, size=size, sort=sort, filters=query_filters)

        self.logger.debug(f"Retrieved {len(result)} DeployVersions")

        return result
    
    async def get_deployVersions_with_versionName(self,column_name: List, conn: Connection) -> list[DeployVersions]:
        """
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.
            column_name (List): 조회할 컬럼 리스트

        Returns:
            str: 배포 버전 결과와 session_data를 포함한 JSON 문자열.
        """
        self.logger.debug(f"Starting get_deployVersions_with_versionName service method")
        
        self.logger.debug(f"Fetching fetch_deployVersions")
        result = await get_deployVersions_with_versionName(conn=conn, column_name=column_name)

        self.logger.debug(f"Retrieved {len(result)} DeployVersions")

        return result
    
    async def check_deployVersions(self):
        """
        실서버 package.json 을 파싱하여서 package 버전 반환.

        Returns:
            str: package.json 에 있는 package 값 반환
        """
        self.logger.debug(f"Starting check_deployVersions service method")
        
        
        return "v1.2.0"
    
    async def make_deployVersions(self, versionName: str, conn: Connection):
        """
        package.json(versionName) 을 기준으로 새로운 버전 생성


        """
        self.logger.debug(f"Starting make_deployVersions service method with versionName: {versionName}")

        result = await fetch_deployVersions_detail(versionName=versionName, conn=conn)
        self.logger.debug(f"result = {result}")

        if result :
            self.logger.error(f"exist versionName={versionName}, craetedAt={result[0]['createdAt']}")

            raise Duplicate(f"exist versionName={versionName}, craetedAt={result[0]['createdAt']}")
        else :
            self.logger.debug("execute ansible")
            ### package.json이랑 준 versionName 이랑 다르면 에러 발생시켜야 하긴 해

            ### ansible 실행 코드
            ### 결과 받아서 insert 하기
            self.logger.debug(f"insert_deployVersions with parameter versionName:{versionName}")
            await insert_deployVersions(versionName=versionName,filpath="filepath",SHA1Value="TEST",conn=conn)

    async def NHN_deployVersions(self,versionId: int, conn: Connection):
        """
        nhn 안정화 버전 배포


        """
        self.logger.debug(f"Starting NHN_deployVersions service method with versionId: {versionId}")        
        try:
            await update_deployVersions(versionId=versionId, conn=conn)
        except Exception as e :
            raise e 

    async def delete_deployVersions(self,versionId: List[int], conn: Connection):
        """
        인자로 주어진 versionId 삭제

        Args:
            versionId (int) : 삭제할 컬럼
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            완료 메세지
        """
        self.logger.debug(f"Starting delete_deployVersions service method with versionId: {versionId}")

        # ansible 실행 코드 후 db업데이트 해야지
        
        try:
            await delete_deployVersions(versionId=versionId, conn=conn)
        except Exception as e :
            raise e 