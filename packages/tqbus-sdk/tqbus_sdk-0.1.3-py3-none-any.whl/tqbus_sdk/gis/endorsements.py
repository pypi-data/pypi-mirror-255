import dataclasses
from typing import List

from tqbus_sdk.tqsystem import TqSystem, TqSystemEnums


@dataclasses.dataclass
class EndorsementService:
    system: TqSystem = dataclasses.field(
        default_factory=lambda: TqSystem(tq_system_enum=TqSystemEnums.GIS)
    )

    def renew_policy_as_is(self, policy_no: str) -> dict:
        url = self.system.base_url + "endorsements/v1/policy-renewal"
        payload = {"policyNo": policy_no}
        data = self.system.request("post", url, json=payload)
        return data

    def enquire_renewal(self, policy_no: str) -> List[dict]:
        url = self.system.base_url + "apis/v2/policies/renewalEnquiry"
        params = {"policyNo": policy_no}
        data = self.system.request("get", url, params=params)
        return data
