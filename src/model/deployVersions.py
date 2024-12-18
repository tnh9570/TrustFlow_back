from pydantic import BaseModel

class DeployVersions(BaseModel):
    versionId: str
    versionName: str
    filePath: str
    SHA1Value: str
    isNhnDeployment: bool
    createdAt: str

class DeployVersionCreate(BaseModel):
    versionName: str
    
class DeployVersionDelete(BaseModel):
    versionId: list[int]
