from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ConcurrencyGroup")


@_attrs_define
class ConcurrencyGroup:
    """
    Attributes:
        concurrency_id (str):
        job_uuids (List[str]):
    """

    concurrency_id: str
    job_uuids: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        concurrency_id = self.concurrency_id
        job_uuids = self.job_uuids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "concurrency_id": concurrency_id,
                "job_uuids": job_uuids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        concurrency_id = d.pop("concurrency_id")

        job_uuids = cast(List[str], d.pop("job_uuids"))

        concurrency_group = cls(
            concurrency_id=concurrency_id,
            job_uuids=job_uuids,
        )

        concurrency_group.additional_properties = d
        return concurrency_group

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
