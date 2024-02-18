from __future__ import annotations

from vectice.api.json.json_type import TJSON


class EntityFileOutput(TJSON):
    @property
    def file_name(self) -> str:
        return str(self["fileName"])
