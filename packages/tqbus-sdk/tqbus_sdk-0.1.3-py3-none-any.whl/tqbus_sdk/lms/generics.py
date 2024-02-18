import dataclasses
import http
from typing import Any

from tqbus_sdk.tqsystem import TqSystem, TqSystemEnums


@dataclasses.dataclass
class GenericIndV1Service:
    system: TqSystem = dataclasses.field(
        default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.IND_V1)
    )

    def request(self, method: http.HTTPMethod, url: str, **kwargs) -> Any:
        url = self.system.base_url + url
        return self.system.request(method=method, url=url, **kwargs)


@dataclasses.dataclass
class GenericIndV2Service:
    system: TqSystem = dataclasses.field(
        default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.IND_V2)
    )

    def request(self, method: http.HTTPMethod, url: str, **kwargs) -> Any:
        url = self.system.base_url + url
        return self.system.request(method=method, url=url, **kwargs)
