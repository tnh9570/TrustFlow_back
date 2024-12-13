from pydantic import BaseModel
from datetime import datetime

class Deployments(BaseModel):
    deploymentId: int
    hospitalId: str
    versionId: int
    reservationTime: datetime
    deployStatus: int
    createdAt: datetime
    updatedAt: datetime