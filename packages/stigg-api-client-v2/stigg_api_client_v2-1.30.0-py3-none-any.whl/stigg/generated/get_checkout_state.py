# Generated by ariadne-codegen on 2024-02-05 10:07
# Source: operations.graphql

from pydantic import Field

from .base_model import BaseModel
from .fragments import CheckoutStateFragment


class GetCheckoutState(BaseModel):
    checkout_state: "GetCheckoutStateCheckoutState" = Field(alias="checkoutState")


class GetCheckoutStateCheckoutState(CheckoutStateFragment):
    pass


GetCheckoutState.update_forward_refs()
GetCheckoutStateCheckoutState.update_forward_refs()
