from __future__ import annotations

from vectice.api.json.json_type import TJSON


class OrganizationConfigOutput(TJSON):
    @property
    def df_statistics_row_threshold(self) -> int:
        return int(self["dfStatisticsRowThreshold"])


class OrgConfigOutput(TJSON):
    @property
    def configuration(self) -> OrganizationConfigOutput:
        return OrganizationConfigOutput(self["organization"]["configuration"])
