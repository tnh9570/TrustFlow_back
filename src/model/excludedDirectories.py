from pydantic import BaseModel
from datetime import datetime

class ExcludedDirectories(BaseModel):
    directoryId: int
    directoryPath: str
    reason: str
    crtime: datetime

class ExcludedDirectoriesCreate(BaseModel):
    directoryPath: str
    reason: str