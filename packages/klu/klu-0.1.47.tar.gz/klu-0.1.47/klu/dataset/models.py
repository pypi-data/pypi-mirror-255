"""
This module provides data models for the Data.
"""

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, Optional

from klu.common.models import BaseEngineModel


@dataclass
class Dataset(BaseEngineModel):
    """
    This class represents the dataset reponse from the API.
    """

    guid: str
    name: str = ""
    description: str = ""
    app: str = ""
    created_by: str = ""

    def __repr__(self):
        return self.generate_repr()

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Dataset":
        data["created_by"] = data.pop("createdById", None)
        return cls._create_instance(
            **{
                "created_at": data.pop("createdAt", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

        base_dict["createdById"] = base_dict.pop("created_by", None)
        return base_dict
