# Generated by ariadne-codegen on 2024-02-05 10:07
# Source: operations.graphql

from pydantic import Field

from .base_model import BaseModel


class ArchiveCustomer(BaseModel):
    archive_customer: "ArchiveCustomerArchiveCustomer" = Field(alias="archiveCustomer")


class ArchiveCustomerArchiveCustomer(BaseModel):
    customer_id: str = Field(alias="customerId")


ArchiveCustomer.update_forward_refs()
ArchiveCustomerArchiveCustomer.update_forward_refs()
