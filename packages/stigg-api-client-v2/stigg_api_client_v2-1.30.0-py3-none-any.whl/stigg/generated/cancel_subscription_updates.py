# Generated by ariadne-codegen on 2024-02-05 10:07
# Source: operations.graphql

from pydantic import Field

from .base_model import BaseModel


class CancelSubscriptionUpdates(BaseModel):
    cancel_schedule: str = Field(alias="cancelSchedule")


CancelSubscriptionUpdates.update_forward_refs()
