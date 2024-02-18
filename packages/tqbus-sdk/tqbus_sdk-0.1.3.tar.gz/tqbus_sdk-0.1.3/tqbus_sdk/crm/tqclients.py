import dataclasses
import datetime
import logging
from typing import List, Optional, Any

import exrex
import requests
from pydantic import BaseModel, Field

from tqbus_sdk.tqsystem import TqSystem, TqSystemEnums, TqDefaultConfig


@dataclasses.dataclass
class ClientType:
    code: int
    name: Optional[str]
    category: Optional[str]
    description: Optional[str]
    type: str


class ClientQueryParam(BaseModel):
    id_registration_no: Optional[str] = Field(default=None)
    passport_no: Optional[str] = Field(default=None)
    client_code: Optional[int] = Field(default=None)
    client_type: Optional[str] = Field(default=None)
    email_address: Optional[str] = Field(default=None)

    name: Optional[str] = Field(default=None)
    page: int = Field(default=0)
    size: int = Field(default=1)
    sht_description: Optional[str] = Field(default=None)
    state_code: Optional[int] = Field(default=None)

    class Config:
        json_encoders = {
            datetime.date: TqDefaultConfig.date_encoder,
            datetime.datetime: TqDefaultConfig.datetime_encoder,
        }
        json_decoders = {
            datetime.date: TqDefaultConfig.date_decoder,
            datetime.datetime: TqDefaultConfig.datetime_decoder,
        }


class Client(BaseModel):
    code: Optional[int] = Field(default=None)
    short_description: Optional[str] = Field(
        default_factory=lambda: exrex.getone("^[A-Z0-9]{5}$")
    )
    name: Optional[str] = Field(default=None)
    other_names: Optional[str] = Field(default=None)
    surname: Optional[str] = Field(default=None)
    id_reg_no: Any = Field(default=None)
    date_of_birth: Optional[datetime.date] = Field(default=None, strict=False)
    PIN: Optional[str] = Field(default=None)
    town_code: Optional[int] = Field(default=544)
    country_code: Optional[int] = Field(default=165)
    zip_code: Optional[int] = Field(default=234)
    date_created: Optional[datetime.datetime] = Field(default=None, strict=False)
    direct_client: Optional[str] = Field(default="N")
    state_code: Optional[int] = Field(default=24)
    branch_code: Optional[int] = Field(default=1)
    payroll_No: Optional[str] = Field(default=None)
    email_address: Optional[str] = Field(default=None)
    telephone: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default="A")
    proposer: Optional[str] = Field(default="Y")
    account_no: Optional[str] = Field(default=None)
    with_effect_from: Optional[datetime.date] = Field(default=None, strict=False)
    with_effect_to: Optional[datetime.datetime] = Field(default=None, strict=False)
    type: str = Field(default="13I")
    gender: Optional[str] = Field(default="B")

    class Config:
        json_encoders = {
            datetime.date: TqDefaultConfig.date_encoder,
            datetime.datetime: TqDefaultConfig.datetime_encoder,
        }
        json_decoders = {
            datetime.date: TqDefaultConfig.date_decoder,
            datetime.datetime: TqDefaultConfig.datetime_decoder,
        }


@dataclasses.dataclass
class ClientService:
    system: TqSystem = dataclasses.field(
        default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.CRM)
    )

    def get(self, query: ClientQueryParam) -> List[Client]:
        url = self.system.base_url + "clients/query"
        params = query.model_dump(
            exclude_none=True,
        )
        data = self.system.request("get", url, params=params)
        return [Client(**_) for _ in data]

    def create(self, client: Client) -> Client:
        url = self.system.base_url + "v3-create-client"
        payload = {"client": client.model_dump(mode="json")}
        try:
            data = self.system.request("post", url=url, json=payload)
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            logging.debug("client creation failsafe, query if created")
            query: ClientQueryParam = ClientQueryParam(
                id_registration_no=client.id_reg_no, email_address=client.email_address
            )
            clients = self.get(query=query)
            logging.debug(f"client creation failsafe, results={clients}")
            if clients:
                data = clients[0]
                return data
            else:
                raise e
        return Client(**data)

    def get_client_types(self) -> List[ClientType]:
        url = self.system.base_url + "client-types"
        data = self.system.request("get", url)
        return [ClientType(**_) for _ in data]
