# Copyright 2023 Agnostiq Inc.

"""
Define cloud QElectron executors.
"""

from typing import Optional, Tuple

from pydantic import BaseModel

# NOTE: support for shot vectors omitted from the cloud executors for now.
# See `override_shots` property on the OS `BaseQExecutor` class for example.


class CloudQExecutor(BaseModel):

    name: str = "cloudq"
    shots: Optional[int] = -1

    def set_shots(self, device_shots):
        """
        Set the shots value of the executor to the value of the QNode device's
        shots if user didn't specify a value.
        """

        if self.shots == -1:
            self.shots = device_shots

    def validate_attrs(self):
        """
        Validate the attributes of the executor and whether they are compatible
        with the QNode's device.
        """

        raise NotImplementedError


class CloudQCluster(CloudQExecutor):

    name: str = "cloudq_cluster"
    executors: Tuple[CloudQExecutor, ...]
    selector: str = "cyclic"

    def validate_attrs(self):
        """
        Validate the attributes of the executor and whether they are compatible
        with the QNode's device.
        """

        for executor in self.executors:
            executor.validate_attrs()
