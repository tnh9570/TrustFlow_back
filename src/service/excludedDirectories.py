from pydantic import BaseModel

class ExcludedDirectories(BaseModel):
    directoryId: int
    directoryPath: str
    reason: str
    crtime: str
