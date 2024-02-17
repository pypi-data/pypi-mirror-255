# Copyright 2023 Agnostiq Inc.


from enum import Enum


class GPU_TYPE(Enum):
    A100 = "a100-80g"
    H100 = "h100"
    A4000 = "a4000"
    A5000 = "a5000"
    A6000 = "a6000"
    A10 = "a10"
    T4 = "t4"
    L40 = "l40"
    V100 = "v100"
