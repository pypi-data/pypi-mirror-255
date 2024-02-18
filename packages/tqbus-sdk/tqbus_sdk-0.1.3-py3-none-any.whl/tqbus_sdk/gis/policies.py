import dataclasses
from typing import List

from tqbus_sdk.tqsystem import TqSystem, TqSystemEnums


@dataclasses.dataclass
class PolicyService:
    system: TqSystem = dataclasses.field(
        default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.GIS)
    )

    def query(self, policy_no: str) -> List[dict]:
        url = self.system.base_url + "apis/v2/policies/policydetails"
        params = {"policyNumber": policy_no}
        data = self.system.request("get", url, params=params)
        return data

    def find(self, policy_no: str) -> dict:
        data = self.query(policy_no=policy_no)
        item = data[0] if data else data
        return item
