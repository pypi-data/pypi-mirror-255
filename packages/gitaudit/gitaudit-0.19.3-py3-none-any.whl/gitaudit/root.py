"""Root module for gitaudit."""

from pydantic import BaseModel, Extra


class GitauditRootModel(BaseModel, extra=Extra.forbid):
    """Base model for all gitaudit models."""
