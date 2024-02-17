import pydantic
import typing


class TimingData(pydantic.BaseModel):
    
    data: typing.Any
    path: str


class UploadIntegrity(pydantic.BaseModel):

    session_id: str
    isilon_path: str
    s3_path: str
    isilon_checksum: str
    s3_checksum: str
    timestamp: str
