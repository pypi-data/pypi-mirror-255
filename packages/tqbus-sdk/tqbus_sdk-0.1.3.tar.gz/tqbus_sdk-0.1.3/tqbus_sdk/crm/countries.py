import dataclasses
from typing import Optional, List, Any

from pydantic import BaseModel

from tqbus_sdk.tqsystem import TqSystem, TqSystemEnums


class Country(BaseModel):
    code: int
    short_description: Optional[str]
    name: Optional[str]
    nationality: Any
    zip_code: Any
    mobile_prefix: Any
    currency_serial: Any


@dataclasses.dataclass
class CountryService:
    system: TqSystem = dataclasses.field(default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.CRM))

    def get(self) -> List[Country]:
        url = self.system.base_url + "countries"
        data = self.system.request("get", url)
        return [Country(**_) for _ in data]
