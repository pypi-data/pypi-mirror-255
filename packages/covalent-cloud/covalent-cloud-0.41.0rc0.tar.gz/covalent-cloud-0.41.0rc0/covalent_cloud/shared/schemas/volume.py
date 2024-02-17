# Copyright 2023 Agnostiq Inc.


"""Models for volumes"""
import re
from typing import Optional

from pydantic import BaseModel, field_validator

from covalent_cloud.shared.classes.exceptions import CovalentSDKError

# Regex pattern for a valid directory name
# ^(/)? - Optionally starts with '/'
# ([\w-]+)$ - Followed by word characters or hyphens, and must end here
VOLUME_NAME_PATTERN = r"^/?([\w-]+)$"


class BaseVolume(BaseModel):
    name: str

    @staticmethod
    def is_volume_name_valid(name):
        match = re.match(VOLUME_NAME_PATTERN, name)
        return match is not None

    @field_validator("name")
    def name_must_be_valid_directory(cls, v):
        match = re.match(VOLUME_NAME_PATTERN, v)
        if not match:
            raise CovalentSDKError(
                "Name must be a valid directory name without subdirectories", "volume/invalid-name"
            )
        return match.group(1)

    @property
    def path(self):
        return f"/{self.name}"

    def __str__(self):
        return self.path


class Volume(BaseVolume):
    """Volume model"""

    id: int
    user_id: str
    efs_access_point_id: str
    name: str
    deployment_id: str
