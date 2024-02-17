# Copyright 2023 Agnostiq Inc.

import uuid
from typing import Dict, List, Optional

from covalent._shared_files.qinfo import QNodeSpecs
from pydantic import BaseModel


class AssetMetadata(BaseModel):
    uri: str
    size: int


class CircuitAssets(BaseModel):
    circuit: Optional[AssetMetadata] = None
    circuit_string: Optional[AssetMetadata] = None
    result: Optional[AssetMetadata] = None
    result_string: Optional[AssetMetadata] = None


class QExecutorSpecs(BaseModel):
    name: str
    attributes: Dict


# Request body for `/register`
class CircuitCreateSchema(BaseModel):
    """Request body for the /register endpoint"""

    python_version: str
    dispatch_id: uuid.UUID
    node_id: int
    circuit_name: str
    circuit_description: str
    qnode_specs: QNodeSpecs

    # Clarify
    allowed_qexecutors: List[QExecutorSpecs]

    # Number of circuits in the batch
    num_circuits: int

    # Object store URIs -- assigned by the server
    assets: Optional[CircuitAssets] = None

    # Unique ID of a circuit -- assigned by the server
    circuit_id: Optional[str] = None

    selector: Optional[str] = None
