# service/deployment.py
from datetime import datetime
from fastapi import Depends, HTTPException
from pymysql.connections import Connection
from model.deployments import Deployments
import logging
from error import Missing
from state import session_data
from data.deployments import (
    fetch_deployments,
    fetch_deployment_detail,
    insert_deployment,
    delete_deployment
)


class DeploymentService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.DeploymentService")

    async def list_deployments(self, conn: Connection) -> list[Deployments]:
        """
        배포 리스트를 가져오고 병원 이름을 추가.
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            Deployments(deployment_with_names): 병원 이름이 포함된 배포 리스트.
        """
        self.logger.debug("Starting list_deployments service method")
        
        self.logger.debug("Fetching deployments from data layer")
        deployments = fetch_deployments(conn)
        
        self.logger.debug(f"Retrieved {len(deployments[:2])} deployments")

        # 리스트 컴프리헨션으로 병원 이름 매칭된 리스트 반환
        return [
            deployment.model_copy(update={"hospitalName": session_data.get(deployment.hospitalId, "알 수 없음")})
            for deployment in deployments
        ]

    async def deployment_detail(self,deploymentId: int, conn: Connection) -> Deployments | None:
        """
        배포 아이디를 기준으로 한개의 ROW 정보를 가져오고 병원 이름을 추가.
        
        Args:
            deploymentId (int): 배포 ID.
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            Deployments(deployment_with_name): 병원 이름이 포함된 배포 상세 정보.
        """

        self.logger.debug(f"Starting deployment_detail service method for deploymentId: {deploymentId}")
        
        self.logger.debug(f"Fetching deployment_detail for deploymentId: {deploymentId}")
        
        try :
            # 배포 정보 가져오기
            deployment = fetch_deployment_detail(conn, deploymentId)  # conn 전달
            self.logger.debug(f"Found deployment_detail for deploymentId: {deploymentId}")

            # 배포 정보의 병원 아이디와 병원 이름 매칭하기
            hospital_name = session_data.get(deployment.hospitalId, "알 수 없음")
            deployment_with_name = deployment.model_copy(update={"hospitalName": hospital_name})

        except Missing as e:
            self.logger.error(f"Service: Deployment not found for ID {deploymentId}")
            raise e  # 그대로 전달
            
        return deployment_with_name

    async def reserve_deployment(self, hospitalId: str, reservationTime, versionId: int, conn: Connection):
        self.logger.debug(f"Starting reserve_deployment service method Input data - hospitalId={hospitalId}, reservationTime={reservationTime}, versionId={versionId}")
        insert_deployment(hospitalId, reservationTime, versionId, conn)

    async def cancel_deployment(self, hospitalId: int):
        delete_deployment(hospitalId)