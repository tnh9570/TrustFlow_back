from pydantic import BaseModel
from datetime import datetime

class DeployVersions(BaseModel):
    versionId: int
    versionName: str
    filePath: str
    SHA1Value: str
    isNhnDeployment: bool
    createdAt: datetime

class DeployVersionCreate(BaseModel):
    versionName: str
    
class DeployVersionDelete(BaseModel):
    versionId: list[int]
