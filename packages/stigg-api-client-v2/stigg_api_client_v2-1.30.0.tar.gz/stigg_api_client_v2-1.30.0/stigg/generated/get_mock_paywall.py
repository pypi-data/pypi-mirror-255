# Generated by ariadne-codegen on 2024-02-05 10:07
# Source: operations.graphql

from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel
from .fragments import MockPaywallPlanFragment, PaywallConfigurationFragment


class GetMockPaywall(BaseModel):
    mock_paywall: "GetMockPaywallMockPaywall" = Field(alias="mockPaywall")


class GetMockPaywallMockPaywall(BaseModel):
    plans: List["GetMockPaywallMockPaywallPlans"]
    configuration: Optional["GetMockPaywallMockPaywallConfiguration"]


class GetMockPaywallMockPaywallPlans(MockPaywallPlanFragment):
    pass


class GetMockPaywallMockPaywallConfiguration(PaywallConfigurationFragment):
    pass


GetMockPaywall.update_forward_refs()
GetMockPaywallMockPaywall.update_forward_refs()
GetMockPaywallMockPaywallPlans.update_forward_refs()
GetMockPaywallMockPaywallConfiguration.update_forward_refs()
