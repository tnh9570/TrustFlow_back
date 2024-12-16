# service/deployment.py
from datetime import datetime
from fastapi import Depends, HTTPException
from pymysql.connections import Connection
from model.deployments import Deployments
import logging
from error import Missing
from state import session_data
from model.deployments import DeploymentCreate, DeploymentsCancled
from data.deployments import (
    fetch_deployments,
    fetch_deployment_detail,
    create_deployment,
    fetch_target_ids,
    update_deployments_to_canceled
)


class DeploymentService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.DeploymentService")

    async def list_deployments(self, conn: Connection) -> list[Deployments]:
        """
        배포 리스트를 가져오고 병원 이름을 추가한 것을 return.
        
        Args:
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            list[Deployments] : 병원 이름이 포함된 배포 리스트.
        """
        self.logger.debug("Starting list_deployments service method")
        
        self.logger.debug("Fetching fetch_deployments from data layer")
        deployments = fetch_deployments(conn)
        
        self.logger.debug(f"Retrieved {len(deployments)} deployments")

        # 리스트 컴프리헨션으로 병원 이름 매칭된 리스트 반환
        return [
            deployment.model_copy(update={"hospitalName": session_data.get(deployment.hospitalId, "알 수 없음")})
            for deployment in deployments
        ]

    async def deployment_detail(self,deploymentId: int, conn: Connection) -> Deployments | None:
        """
        배포 아이디를 기준으로 한개의 ROW 정보를 가져오고 병원 이름을 추가한 것을 return.
        
        Args:
            deploymentId (int): 배포 ID.
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            Deployments : 병원 이름이 포함된 배포 상세 정보.
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

    async def create_deployment(self, hospitalId: str, reservationTime: datetime, versionId: int, conn: Connection):
        """
        배포 예약 로직.

        Args:
            hospitalId (str): 병원 ID.
            reservationTime (datetime): 예약 시간.
            versionId (int): 배포 버전 ID.
            conn (Connection): 데이터베이스 연결 객체.
        """
        self.logger.info(f"Starting create_deployment service method. \
                            Input data: hospitalId={hospitalId}, reservationTime={reservationTime}, versionId={versionId}")
        
        # 예약 시간 검증
        if reservationTime <= datetime.now():
            self.logger.error("Reservation time must be in the future.")
            raise ValueError("Reservation time must be in the future.")

        # 데이터 계층 호출
        try:
            create_deployment(hospitalId, reservationTime, versionId, conn)
        except Exception as e:
            self.logger.error(f"Error in create_deployment: {e}")
            raise

    async def cancel_deployments(self, deploymentIds: list[int], conn: Connection) -> dict:
        """
        배포 ID 리스트의 상태를 취소로 업데이트하고 결과를 반환.

        Args:
            deploymentIds (list[int]): 취소할 배포 ID 리스트.
            conn (Connection): 데이터베이스 연결 객체.

        Returns:
            dict: {"updated": [성공한 ID 리스트], "not_updated": [실패한 ID 리스트]}
        """
        self.logger.debug(f"Starting cancel_deployments service method with IDs: {deploymentIds}")
        
        # 1. 업데이트 대상 ID 가져오기
        target_ids = fetch_target_ids(deploymentIds, conn)
        self.logger.debug(f"Target IDs for update: {target_ids}")

        # 2. 업데이트 수행
        update_deployments_to_canceled(target_ids, conn)
        
        # 결과 계산
        updated = target_ids
        not_updated = list(set(deploymentIds) - set(updated))
        self.logger.debug(f"Updated IDs: {updated}")
        self.logger.debug(f"Not Updated IDs: {not_updated}")
        
        return {"updated": updated, "not_updated": not_updated}
        