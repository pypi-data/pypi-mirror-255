from typing import Optional
from enum import Enum

from pydantic import BaseModel


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    NOT_FETCHED = "not_fetched"


class LicenseVerifiedHttpResponse(BaseModel):
    license_token: str
    token_id: Optional[str]
    token_secret: Optional[str]
    is_valid: bool

    @classmethod
    def error(cls):
        return cls(license_id="", token_id="", token_secret="", is_valid=False)


class DownloadProjectHttpResponse(BaseModel):
    url: Optional[str]
    project_id: Optional[str]
    version: Optional[str]
    is_valid: Optional[bool]
    profile_id: Optional[str]
    profile_status: Optional[ProfileStatus]

    @classmethod
    def error(cls):
        return cls(
            url="",
            project_id="",
            version="",
            is_valid=False,
            profile_id="",
            profile_status=ProfileStatus.NOT_FETCHED,
        )
