from airfold_common.format import Format
from airfold_common.models import AISpec, Spec


class SpecParser:
    def __init__(self, formatter: Format) -> None:
        self.formatter = formatter

    def parse(self, data: dict) -> Spec:
        return Spec.parse_obj(**data)


class ChSpecParser(SpecParser):
    def _parse_ch_spec(self, data: dict) -> Spec | None:
        spec_data = data["spec"]
        type = self.formatter.get_type(spec_data)
        if type == "AISpec":
            ai_spec = AISpec(**spec_data)
            new_data = {"name": data.get("name"), "spec": ai_spec}
            return Spec(**new_data)  # type: ignore
        return None

    def parse(self, data: dict) -> Spec:
        if self.formatter.get_version(data) == "clickhouse.airfold.co/v1":
            res = self._parse_ch_spec(data)
            if res:
                return res
        return super().parse(data)
