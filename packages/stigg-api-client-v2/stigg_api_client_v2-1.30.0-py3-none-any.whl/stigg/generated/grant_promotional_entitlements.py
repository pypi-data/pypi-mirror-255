# Generated by ariadne-codegen on 2024-02-05 10:07
# Source: operations.graphql

from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import PromotionalEntitlementFragment


class GrantPromotionalEntitlements(BaseModel):
    grant_promotional_entitlements: List[
        "GrantPromotionalEntitlementsGrantPromotionalEntitlements"
    ] = Field(alias="grantPromotionalEntitlements")


class GrantPromotionalEntitlementsGrantPromotionalEntitlements(
    PromotionalEntitlementFragment
):
    pass


GrantPromotionalEntitlements.update_forward_refs()
GrantPromotionalEntitlementsGrantPromotionalEntitlements.update_forward_refs()
