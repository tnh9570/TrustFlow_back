from pydantic import BaseModel
from datetime import datetime

class Deployments(BaseModel):
    deploymentId: int
    hospitalId: str
    versionId: int
    versionName: str
    reservationTime: datetime
    deployStatus: int
    createdAt: datetime
    updatedAt: datetime
    hospitalName: str | None = None

class DeploymentCreate(BaseModel):
    hospitalId: str
    reservationTime: datetime
    immediately: bool
    versionId: int

class DeploymentsCancled(BaseModel):
    deploymentIds: list[int]