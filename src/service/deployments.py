# service/deployment.py
from datetime import datetime
from fastapi import Depends, HTTPException
from pymysql.connections import Connection
from model.deployments import Deployments
import logging
from error import Missing
from data.deployments import (
    fetch_deployments,
    fetch_deployment_detail,
    insert_deployment,
    delete_deployment
)


class DeploymentService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.DeploymentService")

    def list_deployments(self, conn: Connection) -> list[Deployments]:
        self.logger.debug("Starting list_deployments service method")
        
        self.logger.debug("Fetching deployments from data layer")
        results = fetch_deployments(conn)
        
        self.logger.debug(f"Retrieved {len(results[:2])} deployments")
        return results

    def deployment_detail(self,deploymentId: int, conn: Connection) -> Deployments | None:
        self.logger.debug(f"Starting deployment_detail service method for deploymentId: {deploymentId}")
        
        self.logger.debug(f"Fetching deployment_detail for deploymentId: {deploymentId}")
        
        try :
            result = fetch_deployment_detail(conn, deploymentId)  # conn 전달
            self.logger.debug(f"Found deployment_detail for deploymentId: {deploymentId}")
        except Missing as e:
            self.logger.error(f"Service: Deployment not found for ID {deploymentId}")
            raise e  # 그대로 전달
            
        return result

    def reserve_deployment(self, hospitalId: str, reservationTime, versionId: int, conn: Connection):
        self.logger.debug(f"Starting reserve_deployment service method Input data - hospitalId={hospitalId}, reservationTime={reservationTime}, versionId={versionId}")
        insert_deployment(hospitalId, reservationTime, versionId, conn)

    def cancel_deployment(self, hospitalId: int):
        delete_deployment(hospitalId)